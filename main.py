import streamlit as st
import time


# Setting page configuration
st.set_page_config(layout="centered", page_title="Income Tax Calculator")
st.markdown("<head> INDIAN INCOME TAX CALCULATOR </head>", unsafe_allow_html=True)
st.markdown(
    "<center> <h1> INDIAN INCOME TAX CALCULATOR </h1> </center>", unsafe_allow_html=True
)
st.markdown(
    "<center> Generate estimated payslips with a few clicks! </center>",
    unsafe_allow_html=True,
)

# Helper functions


def calculate_basepay(gross_salary, bpp):
    return round(gross_salary * bpp / 100)


def calculate_hra(basepay):
    return basepay / 2


def calculate_lta(basepay):
    return basepay / 12


def calculate_splallowance(gross_salary, *args):
    return gross_salary - (sum(args))


def calculate_hra_benefit(rent, basepay, hra, bpp):
    if rent > 0:
        return min(rent - 0.1 * basepay, bpp / 100 * basepay, hra)
    else:
        return 0


def calculate_wealthtax(totalpay, taxval):
    if 5000000 <= totalpay < 10000000:
        return taxval * 0.1
    elif 10000000 <= totalpay < 20000000:
        return taxval * 0.15
    elif 20000000 <= totalpay < 50000000:
        return taxval * 0.25
    elif 50000000 <= totalpay:
        return taxval * 0.37
    else:
        return 0


@st.cache
def generatetax(
    gross_salary,
    bonus_val,
    reimbursement_val,
    basepay,
    hra,
    bpp,
    salary_lta,
    section80c,
    nps,
    rent,
    lta,
    h_loan_principal,
    h_loan_interest,
    employee_pf,
):
    total_income = gross_salary + bonus_val + reimbursement_val
    if nps > 0:
        section80c_final = min(
            section80c + h_loan_principal + nps + employee_pf, 200000
        )
    else:
        section80c_final = min(
            section80c + h_loan_principal + nps + employee_pf, 150000
        )

    hra_benefit = calculate_hra_benefit(rent, basepay, hra, bpp)
    approved_lta = min(lta, salary_lta)
    h_loan_interest = min(h_loan_interest, 200000)
    sd = 50000

    total_savings = section80c_final + hra_benefit + approved_lta + h_loan_interest + sd
    taxable_income = total_income - total_savings

    if taxable_income <= 250000:
        tax = 0
    elif 250000 < taxable_income <= 500000:
        tax = (taxable_income - 250000) * 5 / 100
    elif 500000 < taxable_income <= 1000000:
        tax = ((taxable_income - 500000) * 20 / 100) + 12500
    elif taxable_income > 1000000:
        tax = ((taxable_income - 1000000) * 30 / 100) + 112500

    wealthtax = calculate_wealthtax(taxable_income, tax)
    tax = tax + wealthtax
    tax = tax * 1.04

    return (
        tax,
        total_income,
        total_savings,
        taxable_income,
        hra_benefit,
        approved_lta,
        section80c_final,
        h_loan_interest,
    )


def sectionize(label, figure):
    section = st.columns(2)

    with section[0]:
        st.write(f"{label}")

    with section[1]:
        st.write(f"**Rs. {figure}**")


def generatepayslip(
    gross_salary,
    bonus_val,
    reimbursement_val,
    bpp,
    epf_inclusion_flag,
    section80c,
    nps,
    rent,
    lta,
    h_loan_principal,
    h_loan_interest,
    employee_pf,
    employer_pf,
):
    if epf_inclusion_flag:
        exclusion_msg = "(Employer PF Excluded)"
        gross_salary = gross_salary - employer_pf
    else:
        exclusion_msg = ""

    basepay = calculate_basepay(gross_salary, bpp)
    hra = calculate_hra(basepay)
    salary_lta = calculate_lta(basepay)
    med = 15000  # Constant for the year
    transport = 19200
    splallowance = calculate_splallowance(
        gross_salary, basepay, hra, salary_lta, med, transport
    )
    taxcomponents = generatetax(
        gross_salary,
        bonus_val,
        reimbursement_val,
        basepay,
        hra,
        bpp,
        salary_lta,
        section80c,
        nps,
        rent,
        lta,
        h_loan_principal,
        h_loan_interest,
        employee_pf,
    )
    taxongross = generatetax(
        gross_salary,
        0,
        reimbursement_val,
        basepay,
        hra,
        bpp,
        salary_lta,
        section80c,
        nps,
        rent,
        lta,
        h_loan_principal,
        h_loan_interest,
        employee_pf,
    )

    payslip = st.container()

    with payslip:
        st.write("## Estimated Monthly Salary Slip")
        st.markdown(
            f"<center> <h1> Monthly Salary: {round((gross_salary + reimbursement_val - taxongross[0]-employee_pf)/12,2)} </center> </h3>",
            unsafe_allow_html=True,
        )

        earnings = st.expander("Earnings", expanded=True)
        with earnings:
            sectionize(f"Basic Pay ({bpp}% of Gross)", round(basepay / 12, 2))
            sectionize("House Rental Allowance", round(hra / 12, 2))
            sectionize("Leave Travel Allowance", round(salary_lta / 12, 2))
            sectionize("Medical Allowance", round(med / 12, 2))
            sectionize("Transport Allowance", round(transport / 12, 2))
            sectionize("Special Allowance", round(splallowance / 12, 2))
            sectionize("Monthly Reimbursements", round(reimbursement_val / 12, 2))
            sectionize("_TOTAL_", round((gross_salary + reimbursement_val) / 12, 2))

        deduction = st.expander("Monthly Deductions", expanded=True)
        with deduction:
            sectionize("Employee Provident Fund", round(employee_pf / 12, 2))
            sectionize("Income Tax", round(taxongross[0] / 12, 2))

        taxcalculation = st.expander("Yearly Tax Calculation")
        with taxcalculation:
            st.write("### Yearly Savings/Deductions")
            sectionize("Savings under 80C and NPS", round(taxcomponents[6], 2))
            sectionize("House Rental Benefit", round(taxcomponents[4], 2))
            sectionize("LTA Benefit", round(taxcomponents[5], 2))
            sectionize("Home Loan Interest", round(taxcomponents[7], 2))
            sectionize("Standard Deduction", 50000)
            sectionize("**_TOTAL SAVINGS_**", round(taxcomponents[2], 2))

            st.write("### Yearly Income")
            sectionize(f"_Gross Salary {exclusion_msg}_", round(gross_salary, 2))
            sectionize("_Reimbursements_", round(reimbursement_val, 2))
            sectionize("_Bonus_", round(bonus_val, 2))
            sectionize("**_GROSS INCOME_**", round(taxcomponents[1], 2))
            sectionize(
                "**_TAXABLE INCOME (Gross - Savings)_**", round(taxcomponents[3], 2)
            )
            st.markdown(
                f"<center> <h1> Total Tax: {round(taxcomponents[0],2)} </center> </h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<center> <h3> Total Tax on Gross: {round(taxongross[0],2)} </center> </h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<center> <h3> Total Tax on Bonus: {round(round(taxcomponents[0],2)-round(taxongross[0],2),2)} </center> </h3>",
                unsafe_allow_html=True,
            )


# Income Section
st.markdown("## Income Information")
salaryinfo = st.expander("Click to enter your salary details")

with salaryinfo:
    gross_salary = st.number_input(
        "Enter your yearly gross salary here",
        help="This is you annual gross salary and does not include bonus, employer provident fund contribution or any other benefits",
    )
    bonusinfo = st.columns(2)
    with bonusinfo[0]:
        bonustype = st.selectbox(
            "Enter the bonus type", options=["Percentage of Gross", "Fixed Value"]
        )

    with bonusinfo[1]:
        if bonustype == "Percentage of Gross":
            bonus = st.number_input("Enter your bonus percentage") / 100
            bonus_val = gross_salary * bonus
            total_comp = round(gross_salary + bonus_val)
        elif bonustype == "Fixed Value":
            bonus = st.number_input("Enter your bonus amount")
            bonus_val = bonus
            total_comp = round(gross_salary + bonus)

    reimbursement_val = st.number_input(
        "Enter total yearly value of any reimbursements provided"
    )
    total_comp = total_comp + reimbursement_val


### Provident Fund Section
st.markdown("## Provident Fund Details")
pfinfo = st.expander("Click to enter your provident fund details")

with pfinfo:
    bpp = st.number_input(
        "What percentage of gross salary is your base", max_value=50.0, value=40.00
    )

    epf_inclusion_flag = st.checkbox(
        "Click here if Employer PF is part of total gross compensation"
    )
    if epf_inclusion_flag:
        st.warning(
            "Selecting this will include your employer provident fund contribution as a part of gross salary"
        )

    epe_pf, epr_pf = st.columns(2)

    with epe_pf:
        employee_pf_pct = st.number_input("Employee Provident Fund Percentage") / 100

    with epr_pf:
        employer_pf_pct = st.number_input(
            "Employer Provident Fund Percentage",
        )
        employer_pf = round(
            max(gross_salary * min(employee_pf_pct, 12) * (bpp / 100), 21600)
        )

        if epf_inclusion_flag:
            employee_pf = round(
                max((gross_salary - employer_pf) * employee_pf_pct * (bpp / 100), 21600)
            )
        else:
            employee_pf = round(
                max((gross_salary) * employee_pf_pct * (bpp / 100), 21600)
            )

### Savings and deductions
st.markdown("## Savings Details")
savinginfo = st.expander("Click to enter your saving details")

with savinginfo:
    section80c = st.number_input(
        "Enter your savings under section 80C",
        help="More details about 80C can be found here https://cleartax.in/s/80c-80-deductions",
    )
    nps = st.number_input(
        "Enter your savings under National Pension Scheme",
        help="More details about NPS can be found here https://cleartax.in/s/80c-80-deductions",
    )
    rent = st.number_input(
        "Enter your total yearly rent",
        help="This will be used to calculate tax rebate based on a certain HRA limit",
    )
    lta = st.number_input(
        "Enter your total yearly LTA expense",
        help="This will be used to calculate tax rebate based on a certain LTA limit",
    )
    h_loan_principal = st.number_input(
        "Enter your homeloan principal in a year",
        help="Home loan principles are included in 80C and the same would be covered with a limit of Rs 1.5 lakhs",
    )
    h_loan_interest = st.number_input(
        "Enter your homeloan interest in a year",
        help="Home loan principles are included in 80C and the same would be covered with a limit of Rs 1.5 lakhs",
    )


# buttonarea = st.container()

# with buttonarea:
st.empty()
st.empty()
calculate = st.button("Calculate")

if calculate:
    with st.spinner("Generating Pay Slip..."):
        time.sleep(1.5)
    generatepayslip(
        gross_salary,
        bonus_val,
        reimbursement_val,
        bpp,
        epf_inclusion_flag,
        section80c,
        nps,
        rent,
        lta,
        h_loan_principal,
        h_loan_interest,
        employee_pf,
        employer_pf,
    )


st.markdown(
    "<br> <br> <br> <br> <br> <br>  <br> <br> <br>  <br> <br> <br> <center> Prepared with love by Abhik Chakraborty </center>",
    unsafe_allow_html=True,
)
# Streamlit hack to remove menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
