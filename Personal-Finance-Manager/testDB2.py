from dataBase.FinanceDB import FinanceDB,FinanceService,Direction,SortField
from datetime import datetime
from testTool import print_table
from decimal import Decimal, ROUND_HALF_UP
import calendar
import matplotlib.pyplot as plt
db = FinanceDB(db_url="sqlite:///DB/test.db", echo=False)
service = FinanceService(db)

#print_table(title='abc',rows=service.get_filtered_and_sorted_logs())
#print_table(title='123',rows=service.get_all_categories())




def round_half_up(value, ndigits=2):
    quantize_str = '1.' + '0' * ndigits
    return Decimal(str(value)).quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

def generate_monthly_summary(year, service, Direction):
    """
    產生指定年份的每月收入/支出摘要
    回傳 monthly_summary 字典
    """
    monthly_summary = {}

    for month in range(1, 13):  # 1 到 12 月
        # 取得當月的起始與結束日期
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]  # 該月最後一天
        end_date = datetime(year, month, last_day)

        # 取出資料
        income_logs = service.get_filtered_and_sorted_logs(
            start_date=start_date,
            end_date=end_date,
            direction=Direction.Income
        )

        expenditure_logs = service.get_filtered_and_sorted_logs(
            start_date=start_date,
            end_date=end_date,
            direction=Direction.Expenditure
        )

        total_income = Decimal("0.00")
        total_expenditure = Decimal("0.00")
        income_totals = {}
        expenditure_totals = {}

        # 計算收入
        for log in income_logs:
            amount = round_half_up(log['amount'], 2)
            total_income = round_half_up(total_income + amount, 2)
            category = log['category']
            income_totals[category] = round_half_up(income_totals.get(category, Decimal("0.00")) + amount, 2)

        # 計算支出
        for log in expenditure_logs:
            amount = round_half_up(log['amount'], 2)
            total_expenditure = round_half_up(total_expenditure + amount, 2)
            category = log['category']
            expenditure_totals[category] = round_half_up(expenditure_totals.get(category, Decimal("0.00")) + amount, 2)

        # 計算淨額
        remaining_amount = round_half_up(total_income - total_expenditure, 2)

        # 三個字典分開
        summary_totals = {
            "Totals": {
                "Total Income": total_income,
                "Total Expenditure": total_expenditure,
                "Remaining Amount": remaining_amount
            },
            "Income Categories": income_totals,
            "Expenditure Categories": expenditure_totals
        }

        # 存入每月摘要
        monthly_summary[f"{year}-{month:02d}"] = summary_totals

    return monthly_summary


def print_monthly_summary(monthly_summary):
    """
    顯示每月的摘要結果
    """
    for month, summary in monthly_summary.items():
        print(f"\nSummary for {month}:")
        print("Income Categories:")
        for cat, val in summary["Income Categories"].items():
            print(f"  {cat}: {val:.2f}")
        print("Expenditure Categories:")
        for cat, val in summary["Expenditure Categories"].items():
            print(f"  {cat}: {val:.2f}")
        print("Totals:")
        for key, val in summary["Totals"].items():
            print(f"  {key}: {val:.2f}")

        # 直接印出字典形式
        #print("\n字典輸出:")
        #print("Income Categories:", summary["Income Categories"])
        #print("Expenditure Categories:", summary["Expenditure Categories"])
        #print("Totals:", summary["Totals"])


def plot_pie_chart(month_key, summary, category_type="Income"):
    """
    畫圓餅圖
    month_key: 字串，例如 "2025-10"
    summary: monthly_summary[month_key] 的字典
    category_type: "Income" 或 "Expenditure"
    """
    if category_type == "Income":
        data = summary["Income Categories"]
        title = f"Income Categories for {month_key}"
    elif category_type == "Expenditure":
        data = summary["Expenditure Categories"]
        title = f"Expenditure Categories for {month_key}"
    else:
        raise ValueError("category_type 必須是 'Income' 或 'Expenditure'")

    if not data:  # 避免空字典
        print(f"{title} 沒有資料，無法繪製圓餅圖")
        return

    plt.figure(figsize=(6,6))
    plt.pie(
        data.values(),
        labels=data.keys(),
        autopct="%1.1f%%"
    )
    plt.title(title)
    plt.show()


# === 主程式 ===
year = 2025
monthly_summary = generate_monthly_summary(year, service, Direction)

# 印出每月摘要
print_monthly_summary(monthly_summary)

# 手動輸入月份並畫圖
month = int(input("請輸入月份 (1-12): "))
month_key = f"{year}-{month:02d}"
summary = monthly_summary[month_key]

plot_pie_chart(month_key, summary, category_type="Income")
plot_pie_chart(month_key, summary, category_type="Expenditure")





# print(sum(service.get_filtered_and_sorted_logs(start_date=datetime(2025,10,1),end_date=datetime(2025,10,31),direction=Direction.Income)))
#print(dict_category)
