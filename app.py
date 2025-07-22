
import streamlit as st
from fpdf import FPDF

def calculate_apex_property_costs(
    property_value,
    seller_down_payment,
    bank_interest_rate,
    loan_term_years,
    seller_interest_rate,
    seller_term_months,
    seller_monthly_payment,
    hold_years
):
    bank_loan = 0.65 * property_value
    seller_finance = property_value - seller_down_payment
    pml_fee = 0.10 * seller_down_payment
    net_cash_pre_merit = bank_loan - seller_down_payment - pml_fee
    home_merit_fee = 0.10 * net_cash_pre_merit
    total_fees = pml_fee + home_merit_fee
    net_cash_final = net_cash_pre_merit - home_merit_fee

    monthly_rate = bank_interest_rate / 12
    total_payments = loan_term_years * 12
    months_held = hold_years * 12

    monthly_bank_payment = bank_loan * (monthly_rate * (1 + monthly_rate)**total_payments) / (
        (1 + monthly_rate)**total_payments - 1)
    total_paid_bank = monthly_bank_payment * months_held
    remaining_balance_bank = bank_loan * (
        ((1 + monthly_rate)**total_payments - (1 + monthly_rate)**months_held) /
        ((1 + monthly_rate)**total_payments - 1))
    principal_paid_bank = bank_loan - remaining_balance_bank
    interest_paid_bank = total_paid_bank - principal_paid_bank

    total_paid_seller = seller_monthly_payment * seller_term_months
    balloon_payment = max(seller_finance - (seller_monthly_payment * seller_term_months), 0)
    total_seller_paid = total_paid_seller + balloon_payment
    seller_interest_paid = max(total_seller_paid - seller_finance, 0)

    total_cost = interest_paid_bank + total_fees + seller_interest_paid
    final_value = net_cash_final + total_cost
    annual_cost = (final_value / net_cash_final)**(1 / hold_years) - 1

    return {
        "bank_loan": bank_loan,
        "seller_finance": seller_finance,
        "pml_fee": pml_fee,
        "net_cash_pre_merit": net_cash_pre_merit,
        "home_merit_fee": home_merit_fee,
        "net_cash_final": net_cash_final,
        "total_fees": total_fees,
        "monthly_bank_payment": monthly_bank_payment,
        "interest_paid_bank": interest_paid_bank,
        "remaining_balance_bank": remaining_balance_bank,
        "balloon_payment": balloon_payment,
        "seller_interest_paid": seller_interest_paid,
        "annual_cost_percent": annual_cost * 100
    }

def export_to_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Apex Property Group — Deal Analysis", ln=True, align='C')
    pdf.set_font("Arial", size=12)

    for key, value in results.items():
        pdf.cell(200, 10, f"{key.replace('_', ' ').title()}: ${value:,.2f}" if 'percent' not in key else f"{key.replace('_', ' ').title()}: {value:.2f}%", ln=True)

    output_path = "/mnt/data/apex_analysis_report.pdf"
    pdf.output(output_path)
    return output_path

st.markdown("""<style>
    .main { background-color: #000000; color: white; }
    html, body, [class*="css"]  { background-color: #000000; color: white !important; }
    h1, h2, h3, h4, h5, h6, label, .stTextInput label, .stSidebar label {
        color: white !important;
    }
    .stButton>button { background-color: #FF6F00; color: white; border: none; }
    .stSidebar { background-color: #111111; color: white; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#FF6F00;'>Apex Property Group — Deal Analyzer</h1>", unsafe_allow_html=True)

st.sidebar.header("Deal Info")
property_value = st.sidebar.number_input("Property Value", value=1200000)
seller_down_payment = st.sidebar.number_input("Seller Down Payment", value=330000)
bank_interest_rate = st.sidebar.number_input("Bank Interest Rate (e.g. 0.075)", value=0.075)
loan_term_years = st.sidebar.number_input("Bank Loan Term (Years)", value=30)
seller_interest_rate = st.sidebar.number_input("Seller Interest Rate", value=0.0)
seller_term_months = st.sidebar.number_input("Seller Term (Months)", value=96)
seller_monthly_payment = st.sidebar.number_input("Monthly Payment to Seller", value=2400)
hold_years = st.sidebar.number_input("Hold Period (Years)", value=8)

if st.sidebar.button("Calculate"):
    results = calculate_apex_property_costs(
        property_value,
        seller_down_payment,
        bank_interest_rate,
        loan_term_years,
        seller_interest_rate,
        seller_term_months,
        seller_monthly_payment,
        hold_years
    )

    st.subheader("📊 Results")
    for key, value in results.items():
        label = key.replace('_', ' ').title()
        if 'percent' in key:
            st.write(f"**{label}**: {value:.2f}%")
        else:
            st.write(f"**{label}**: ${value:,.2f}")

    if st.button("📄 Export to PDF"):
        pdf_path = export_to_pdf(results)
        with open(pdf_path, "rb") as file:
            btn = st.download_button(label="Download Analysis PDF", data=file, file_name="apex_analysis_report.pdf", mime="application/pdf")
