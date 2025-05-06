from PIL import Image
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Expense Splitter", layout="centered")
st.title("🏠 Expense Splitter App")
st.write("Add and track group expenses. Split like a pro, no more awkward 'who owes who' moments!")

# Initialize session state
if "roommates" not in st.session_state:
    st.session_state.roommates = []
if "roommates_registered" not in st.session_state:
    st.session_state.roommates_registered = False
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# Register roommates
if not st.session_state.roommates_registered:
    st.subheader("👥 Register Your Roommates")
    num_people = st.number_input("How many people are sharing expenses?", min_value=2, max_value=20, step=1)
    roommate_names = []

    with st.form("register_form"):
        for i in range(int(num_people)):
            name = st.text_input(f"Enter name for person {i + 1}", key=f"roommate_{i}")
            roommate_names.append(name)
        register_btn = st.form_submit_button("Register Roommates")

        if register_btn:
            if all(name.strip() != "" for name in roommate_names):
                st.session_state.roommates = roommate_names
                st.session_state.roommates_registered = True
                st.experimental_rerun()
            else:
                st.warning("Please fill all the names to register.")
else:
    roommates = st.session_state.roommates
    st.sidebar.write("👥 Roommates:")
    st.sidebar.write(", ".join(roommates))

    st.subheader("🧾 Add an Expense")

    with st.form("expense_form", clear_on_submit=True):
        spender = st.selectbox("Who Paid?", roommates)
        amount = st.number_input("Amount Spent ($)", min_value=0.01, step=0.01)
        description = st.text_input("Description of Expense", placeholder="e.g., Pizza, Groceries")
        shared_by = st.multiselect("Shared Among", roommates, default=roommates)
        add_expense_btn = st.form_submit_button("Add Expense")

        if add_expense_btn:
            st.session_state.expenses.append({
                "Spender": spender,
                "Amount": amount,
                "Description": description,
                "Shared By": shared_by
            })
            st.success(f"✅ Added: {spender} paid ${amount:.2f} for '{description}' shared with {len(shared_by)} people.")

    # Show expense log
    if st.session_state.expenses:
        st.subheader("📒 Expense Log")
        df = pd.DataFrame(st.session_state.expenses)
        df["Shared With"] = df["Shared By"].apply(lambda x: ", ".join(x))
        st.dataframe(df[["Spender", "Amount", "Description", "Shared With"]])

        st.subheader("📊 Balances")
        paid = {person: 0.0 for person in roommates}
        owes = {person: 0.0 for person in roommates}

        for exp in st.session_state.expenses:
            amt = exp["Amount"]
            payer = exp["Spender"]
            shared = exp["Shared By"]
            share_amt = amt / len(shared)

            paid[payer] += amt
            for person in shared:
                owes[person] += share_amt

        balances = {person: round(paid[person] - owes[person], 2) for person in roommates}
        balance_df = pd.DataFrame(list(balances.items()), columns=["Roommate", "Net Balance ($)"])
        st.dataframe(balance_df.style.applymap(lambda val: 'color: green' if val > 0 else 'color: red', subset=["Net Balance ($)"]))

        st.subheader("💸 Who Owes Whom")
        creditors = {p: b for p, b in balances.items() if b > 0}
        debtors = {p: -b for p, b in balances.items() if b < 0}

        settlements = []
        for debtor, debt_amt in debtors.items():
            for creditor, credit_amt in creditors.items():
                if debt_amt == 0:
                    break
                if credit_amt == 0:
                    continue
                transfer = min(debt_amt, credit_amt)
                debt_amt -= transfer
                creditors[creditor] -= transfer
                settlements.append(f"{debtor} owes {creditor} ${transfer:.2f}")

        if settlements:
            for s in settlements:
                st.write("🔁", s)
        else:
            st.success("✅ All settled up! No debts at the moment.")
    else:
        st.info("No expenses added yet. Start recording above.")
