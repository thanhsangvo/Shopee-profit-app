import streamlit as st
import pandas as pd
import plotly.express as px

# Setup page config
st.set_page_config(
    page_title="Shopee Profit Calculator",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile friendliness and modern look
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        text-align: center;
        color: #EE4D2D; /* Shopee Orange */
        font-weight: 700;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("💰 Tính Lợi Nhuận Shopee")
st.markdown("---")

# --- Input Section ---
with st.expander("📝 Nhập liệu thông tin sản phẩm", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        selling_price = st.number_input("Giá bán (VNĐ)", min_value=0, value=100000, step=1000)
        cost_price = st.number_input("Giá vốn (VNĐ)", min_value=0, value=50000, step=1000)
        fixed_fee = st.number_input("Phí cố định (VNĐ)", min_value=0, value=0, step=1000, help="Phí đóng gói, nhân sự, v.v.")

    with col2:
        payment_fee_percent = st.number_input("Phí thanh toán (%)", min_value=0.0, value=4.0, step=0.1)
        platform_fee_percent = st.number_input("Phí sàn (%)", min_value=0.0, value=5.0, step=0.1)
        freeship_fee_percent = st.number_input("Phí Freeship Xtra (%)", min_value=0.0, value=6.0, step=0.1)

# --- Calculation Logic ---
tax_rate = 1.5 / 100
tax_amount = selling_price * tax_rate

payment_fee_amount = selling_price * (payment_fee_percent / 100)
platform_fee_amount = selling_price * (platform_fee_percent / 100)
freeship_fee_amount = selling_price * (freeship_fee_percent / 100)

total_platform_fees = payment_fee_amount + platform_fee_amount + freeship_fee_amount + fixed_fee
total_cost = cost_price + total_platform_fees + tax_amount
profit = selling_price - total_cost

if selling_price > 0:
    profit_margin = (profit / selling_price) * 100
else:
    profit_margin = 0

# --- Display Results ---
st.markdown("### 📊 Kết quả phân tích")

# Metrics
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Doanh thu", f"{selling_price:,.0f} đ")
with m2:
    st.metric("Lợi nhuận", f"{profit:,.0f} đ", delta_color="normal" if profit >= 0 else "inverse")
with m3:
    st.metric("% Lợi nhuận", f"{profit_margin:.2f}%", delta_color="normal" if profit >= 0 else "inverse")

st.divider()

# Visualization
st.subheader("🍰 Phân bổ chi phí")

# Data for Pie Chart
data = {
    "Category": ["Giá vốn", "Tổng phí sàn & vận hành", "Thuế (1.5%)", "Lợi nhuận"],
    "Amount": [cost_price, total_platform_fees, tax_amount, max(0, profit)] 
    # Determine if we want to show negative profit or just cap at 0 for pie chart visualization logic.
    # Usually pie charts don't show negative values. 
    # If profit is negative, the pie chart sums will exceed revenue, which is weird but technically we are visualizing "Where the money goes".
    # A better way for pie chart of revenue distribution:
    # Revenue = Cost + Fees + Tax + Profit. 
    # If Profit is negative, Revenue + Loss = Cost + Fees + Tax.
    # Let's stick to simple distribution of revenue components. If profit is negative, it won't be shown in the pie or will be 0.
}

df_chart = pd.DataFrame(data)

# If profit is negative, we can add a 'Loss' category or just handle it gracefully.
# For simplicity in this chart, we handle negative profit by excluding it from the "Revenue Distribution" concept or showing it differently.
# Let's strictly show components of Revenue. Calculate total expenses first.
total_expenses = cost_price + total_platform_fees + tax_amount

if profit >= 0:
    fig = px.pie(
        df_chart, 
        values='Amount', 
        names='Category', 
        title='Cơ cấu doanh thu',
        hole=0.4,
        color='Category',
        color_discrete_map={
            "Lợi nhuận": "#2ECC71",
            "Giá vốn": "#3498DB",
            "Tổng phí sàn & vận hành": "#E74C3C",
            "Thuế (1.5%)": "#F1C40F"
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"⚠️ Bạn đang lỗ: {abs(profit):,.0f} đ")
    # Show cost breakdown regardless of profit
    cost_data = {
        "Category": ["Giá vốn", "Tổng phí sàn & vận hành", "Thuế (1.5%)"],
        "Amount": [cost_price, total_platform_fees, tax_amount]
    }
    df_cost = pd.DataFrame(cost_data)
    fig = px.pie(
        df_cost, 
        values='Amount', 
        names='Category', 
        title='Cơ cấu chi phí (Vượt quá doanh thu)',
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# Detailed Table
with st.expander("Chi tiết các loại phí"):
    st.write(pd.DataFrame({
        "Loại phí": ["Phí thanh toán", "Phí sàn", "Phí Freeship Xtra", "Phí cố định", "Thuế"],
        "Số tiền": [payment_fee_amount, platform_fee_amount, freeship_fee_amount, fixed_fee, tax_amount]
    }).style.format({"Số tiền": "{:,.0f} đ"}))

