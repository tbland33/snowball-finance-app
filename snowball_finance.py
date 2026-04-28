import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Snowball Finance", layout="wide")
st.title("❄️ Snowball Finance")
st.caption("Personal Budget Tracker + Debt Snowball Simulator")

# Session State
if "budget" not in st.session_state:
    st.session_state.budget = {"income": 4500, "expenses": {}}
if "debts" not in st.session_state:
    st.session_state.debts = pd.DataFrame(columns=["Debt Name", "Balance", "Min Payment"])

tab1, tab2, tab3 = st.tabs(["📊 Budget Tracker", "❄️ Debt Snowball", "📈 Dashboard"])

with tab1:
    st.subheader("Monthly Income & Expenses")
    income = st.number_input("Monthly Take-Home Income ($)", value=st.session_state.budget["income"], step=100)
    st.session_state.budget["income"] = income

    st.write("### Add Expenses")
    col1, col2 = st.columns(2)
    with col1:
        exp_name = st.text_input("Expense Name")
    with col2:
        exp_amount = st.number_input("Amount ($)", step=10.0, value=0.0)
    
    if st.button("Add Expense") and exp_name:
        st.session_state.budget["expenses"][exp_name] = exp_amount
        st.success(f"Added {exp_name}")

    if st.session_state.budget["expenses"]:
        exp_df = pd.DataFrame(list(st.session_state.budget["expenses"].items()), columns=["Expense", "Amount"])
        edited = st.data_editor(exp_df, num_rows="dynamic", use_container_width=True)
        st.session_state.budget["expenses"] = dict(zip(edited["Expense"], edited["Amount"]))

    total_exp = sum(st.session_state.budget["expenses"].values())
    st.metric("Net Cash Flow", f"${income - total_exp:,.0f}")

with tab2:
    st.subheader("Debt Snowball Simulator")
    colA, colB, colC = st.columns(3)
    with colA:
        debt_name = st.text_input("Debt Name (e.g. Credit Card)")
    with colB:
        balance = st.number_input("Current Balance ($)", step=100.0, value=0.0)
    with colC:
        min_pay = st.number_input("Minimum Payment ($)", step=10.0, value=0.0)
    
    if st.button("Add Debt") and debt_name and balance > 0:
        new_row = pd.DataFrame([{"Debt Name": debt_name, "Balance": balance, "Min Payment": min_pay}])
        st.session_state.debts = pd.concat([st.session_state.debts, new_row], ignore_index=True)
        st.success("Debt added!")

    if not st.session_state.debts.empty:
        edited_debts = st.data_editor(st.session_state.debts, num_rows="dynamic", use_container_width=True)
        st.session_state.debts = edited_debts

        extra = st.slider("Extra Money to Throw at Debt Each Month ($)", 0, 1000, 300, step=50)
        
        if st.button("🚀 Run Snowball Simulation"):
            debts = edited_debts.copy()
            debts = debts[debts["Balance"] > 0].sort_values("Balance").reset_index(drop=True)
            
            if debts.empty:
                st.info("🎉 You have no debt! You're already debt-free.")
            else:
                months = 0
                remaining = []
                while debts["Balance"].sum() > 0 and months < 360:
                    months += 1
                    extra_left = extra
                    for i in range(len(debts)):
                        if debts.loc[i, "Balance"] <= 0:
                            continue
                        pay = min(debts.loc[i, "Min Payment"], debts.loc[i, "Balance"])
                        debts.loc[i, "Balance"] -= pay
                        if i == 0 and extra_left > 0:
                            ex_pay = min(extra_left, debts.loc[i, "Balance"])
                            debts.loc[i, "Balance"] -= ex_pay
                            extra_left -= ex_pay
                    remaining.append(debts["Balance"].sum())
                    debts = debts[debts["Balance"] > 0].reset_index(drop=True)
                
                st.success(f"✅ Debt-free in **{months} months** (${extra} extra/month)!")
                fig = px.line(x=list(range(1, months+1)), y=remaining, 
                             labels={"x": "Month", "y": "Remaining Debt ($)"})
                fig.update_layout(title="Your Debt Snowball Progress")
                st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Overview")
    if st.session_state.budget["expenses"]:
        exp_df = pd.DataFrame(list(st.session_state.budget["expenses"].items()), columns=["Category", "Amount"])
        st.plotly_chart(px.pie(exp_df, names="Category", values="Amount", title="Where Your Money Goes"), use_container_width=True)
    
    if not st.session_state.debts.empty:
        total_debt = st.session_state.debts["Balance"].sum()
        st.metric("Total Debt Right Now", f"${total_debt:,.0f}")

st.caption("Built live with Grok • Version 1.2")
