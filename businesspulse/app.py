from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import math
import os
import random

app = Flask(__name__)
app.secret_key = 'businesspulse_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///businesspulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─── Database Model ────────────────────────────────────────────────────────────
class BusinessEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)
    customers = db.Column(db.Integer, nullable=False)
    avg_bill = db.Column(db.Float, nullable=False)
    best_item = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'owner_name': self.owner_name,
            'business_type': self.business_type,
            'city': self.city,
            'revenue': self.revenue,
            'expenses': self.expenses,
            'customers': self.customers,
            'avg_bill': self.avg_bill,
            'best_item': self.best_item,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p')
        }


# ─── Analytics Engine ──────────────────────────────────────────────────────────
def calculate_analytics(data):
    revenue = float(data['revenue'])
    expenses = float(data['expenses'])
    customers = int(data['customers'])
    avg_bill = float(data['avg_bill'])

    profit = revenue - expenses
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    revenue_per_customer = revenue / customers if customers > 0 else 0
    est_monthly_revenue = revenue * 26  # 26 working days
    est_monthly_profit = profit * 26
    expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0

    # Business Health Score (0-100)
    score = 0
    score += min(30, profit_margin * 1.5)           # Profit margin (max 30)
    score += min(20, (customers / 10) * 2)           # Customer volume (max 20)
    score += min(20, min(revenue / 1000, 1) * 20)   # Revenue strength (max 20)
    score += 15 if profit > 0 else 0                 # Profitability bonus
    score += min(15, (1 - expense_ratio / 100) * 15) # Expense efficiency (max 15)
    score = max(0, min(100, score))

    if score >= 80:
        health_label = "Excellent"
        health_color = "#10b981"
        health_icon = "fa-trophy"
        health_badge = "success"
    elif score >= 60:
        health_label = "Good"
        health_color = "#3b82f6"
        health_icon = "fa-thumbs-up"
        health_badge = "primary"
    elif score >= 40:
        health_label = "Average"
        health_color = "#f59e0b"
        health_icon = "fa-chart-line"
        health_badge = "warning"
    else:
        health_label = "Needs Improvement"
        health_color = "#ef4444"
        health_icon = "fa-exclamation-triangle"
        health_badge = "danger"

    # Weekly trend (simulated realistic variation around today's data)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    today_idx = datetime.now().weekday()
    weekly_revenue = []
    weekly_expense = []
    for i, day in enumerate(days):
        if i < today_idx:
            factor = random.uniform(0.75, 1.25)
            weekly_revenue.append(round(revenue * factor, 2))
            weekly_expense.append(round(expenses * factor * random.uniform(0.85, 1.1), 2))
        elif i == today_idx:
            weekly_revenue.append(round(revenue, 2))
            weekly_expense.append(round(expenses, 2))
        else:
            weekly_revenue.append(None)
            weekly_expense.append(None)

    # Monthly projection
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = datetime.now().month - 1
    monthly_revenue = []
    monthly_profit = []
    for i in range(12):
        if i < current_month:
            growth = 1 + (i - current_month) * 0.02
            factor = random.uniform(0.8, 1.2) * growth
            m_rev = est_monthly_revenue * factor
            m_prof = m_rev * (profit_margin / 100) * random.uniform(0.9, 1.1)
            monthly_revenue.append(round(m_rev, 2))
            monthly_profit.append(round(m_prof, 2))
        elif i == current_month:
            monthly_revenue.append(round(est_monthly_revenue, 2))
            monthly_profit.append(round(est_monthly_profit, 2))
        else:
            proj_factor = 1 + (i - current_month) * 0.03
            monthly_revenue.append(round(est_monthly_revenue * proj_factor, 2))
            monthly_profit.append(round(est_monthly_profit * proj_factor, 2))

    # Expense breakdown (intelligent distribution)
    business_type = data.get('business_type', '').lower()
    if 'restaurant' in business_type or 'cafe' in business_type or 'biryani' in business_type or 'bakery' in business_type or 'juice' in business_type:
        expense_labels = ['Raw Materials', 'Staff Wages', 'Rent', 'Utilities', 'Packaging', 'Misc']
        expense_weights = [0.40, 0.25, 0.18, 0.08, 0.05, 0.04]
    elif 'medical' in business_type or 'pharmacy' in business_type:
        expense_labels = ['Stock/Medicines', 'Staff', 'Rent', 'Utilities', 'Licenses', 'Misc']
        expense_weights = [0.50, 0.20, 0.15, 0.07, 0.05, 0.03]
    elif 'grocery' in business_type or 'supermarket' in business_type:
        expense_labels = ['Stock Purchase', 'Staff', 'Rent', 'Utilities', 'Logistics', 'Misc']
        expense_weights = [0.55, 0.18, 0.14, 0.07, 0.03, 0.03]
    elif 'salon' in business_type or 'beauty' in business_type:
        expense_labels = ['Products', 'Staff', 'Rent', 'Utilities', 'Equipment', 'Misc']
        expense_weights = [0.30, 0.30, 0.20, 0.10, 0.06, 0.04]
    elif 'cloth' in business_type or 'fashion' in business_type:
        expense_labels = ['Inventory', 'Staff', 'Rent', 'Utilities', 'Marketing', 'Misc']
        expense_weights = [0.50, 0.20, 0.18, 0.06, 0.04, 0.02]
    elif 'mobile' in business_type or 'electronics' in business_type:
        expense_labels = ['Stock', 'Staff', 'Rent', 'Utilities', 'Repair Parts', 'Misc']
        expense_weights = [0.55, 0.18, 0.14, 0.07, 0.04, 0.02]
    elif 'hardware' in business_type:
        expense_labels = ['Stock/Materials', 'Staff', 'Rent', 'Utilities', 'Transport', 'Misc']
        expense_weights = [0.52, 0.18, 0.15, 0.07, 0.05, 0.03]
    else:
        expense_labels = ['Stock/Inventory', 'Staff', 'Rent', 'Utilities', 'Marketing', 'Misc']
        expense_weights = [0.45, 0.22, 0.17, 0.08, 0.05, 0.03]

    expense_breakdown = [round(expenses * w, 2) for w in expense_weights]

    # AI Insights
    insights = generate_insights(data, profit, profit_margin, revenue_per_customer, expense_ratio, score)

    # Business Diagnosis (Flaws + Fixes)
    diagnosis = generate_diagnosis(data, profit, profit_margin, revenue_per_customer, expense_ratio, score)

    return {
        'revenue': revenue,
        'expenses': expenses,
        'profit': profit,
        'profit_margin': round(profit_margin, 1),
        'revenue_per_customer': round(revenue_per_customer, 2),
        'avg_bill': avg_bill,
        'est_monthly_revenue': round(est_monthly_revenue, 2),
        'est_monthly_profit': round(est_monthly_profit, 2),
        'health_score': round(score, 1),
        'health_label': health_label,
        'health_color': health_color,
        'health_icon': health_icon,
        'health_badge': health_badge,
        'expense_ratio': round(expense_ratio, 1),
        'weekly_revenue': weekly_revenue,
        'weekly_expense': weekly_expense,
        'weekly_days': days,
        'monthly_revenue': monthly_revenue,
        'monthly_profit': monthly_profit,
        'months': months,
        'expense_labels': expense_labels,
        'expense_breakdown': expense_breakdown,
        'insights': insights,
        'diagnosis': diagnosis,
        'customers': customers,
        'best_item': data['best_item'],
        'business_name': data['business_name'],
        'owner_name': data['owner_name'],
        'business_type': data['business_type'],
        'city': data['city'],
        'generated_at': datetime.now().strftime('%d %B %Y, %I:%M %p')
    }


def generate_insights(data, profit, profit_margin, revenue_per_customer, expense_ratio, health_score):
    revenue = float(data['revenue'])
    expenses = float(data['expenses'])
    customers = int(data['customers'])
    avg_bill = float(data['avg_bill'])
    best_item = data['best_item']
    business_type = data.get('business_type', 'Business')

    insights = []

    # Insight 1: Average Bill Upsell
    target_bill = round(avg_bill * 1.15, 0)
    extra_revenue = round((target_bill - avg_bill) * customers * 26, 2)
    insights.append({
        'icon': 'fa-receipt',
        'color': '#3b82f6',
        'bg': 'rgba(59,130,246,0.1)',
        'title': 'Increase Average Bill Value',
        'text': f'Your current average bill is ₹{avg_bill:,.0f}. Encouraging customers to add just one more item could push it to ₹{target_bill:,.0f}, generating an additional ₹{extra_revenue:,.0f} per month.',
        'impact': 'High Impact'
    })

    # Insight 2: Expense Optimization
    if expense_ratio > 60:
        savings = round(expenses * 0.08, 2)
        insights.append({
            'icon': 'fa-scissors',
            'color': '#ef4444',
            'bg': 'rgba(239,68,68,0.1)',
            'title': 'Reduce Operating Expenses',
            'text': f'Your expenses are {expense_ratio:.1f}% of revenue, which is above the industry optimal of 55%. A targeted 8% cost reduction would save ₹{savings:,.0f} daily (₹{savings*26:,.0f}/month).',
            'impact': 'High Impact'
        })
    else:
        insights.append({
            'icon': 'fa-piggy-bank',
            'color': '#10b981',
            'bg': 'rgba(16,185,129,0.1)',
            'title': 'Strong Expense Control',
            'text': f'Your expense ratio of {expense_ratio:.1f}% is well managed. Maintain this discipline and redirect savings into marketing or stock expansion to accelerate growth.',
            'impact': 'Maintain'
        })

    # Insight 3: Best Seller Promotion
    insights.append({
        'icon': 'fa-star',
        'color': '#f59e0b',
        'bg': 'rgba(245,158,11,0.1)',
        'title': f'Promote Your Star Product: {best_item}',
        'text': f'"{best_item}" is your top seller. Create a visible display, offer a loyalty reward for repeat purchases, or bundle it with a complementary item to increase both volume and margin.',
        'impact': 'Medium Impact'
    })

    # Insight 4: Customer Retention
    retention_revenue = round(customers * 0.2 * avg_bill * 26, 2)
    insights.append({
        'icon': 'fa-users',
        'color': '#8b5cf6',
        'bg': 'rgba(139,92,246,0.1)',
        'title': 'Launch a Customer Loyalty Program',
        'text': f'Retaining just 20% more of your {customers} daily customers through a simple loyalty card or WhatsApp group could add ₹{retention_revenue:,.0f} per month in recurring revenue.',
        'impact': 'High Impact'
    })

    # Insight 5: Digital Presence
    insights.append({
        'icon': 'fa-mobile-alt',
        'color': '#06b6d4',
        'bg': 'rgba(6,182,212,0.1)',
        'title': 'Build a Digital Presence',
        'text': f'Businesses with an active Google Business Profile and WhatsApp catalogue see 30–40% more walk-in customers. List {data["business_name"]} online to reach customers searching locally in {data["city"]}.',
        'impact': 'Medium Impact'
    })

    # Insight 6: Revenue-based insight
    if profit_margin < 20:
        insights.append({
            'icon': 'fa-chart-line',
            'color': '#f97316',
            'bg': 'rgba(249,115,22,0.1)',
            'title': 'Improve Profit Margin',
            'text': f'Your profit margin is {profit_margin:.1f}%. The industry benchmark for {business_type} is 20–35%. Focus on premium product offerings and reducing low-margin items to reach this target.',
            'impact': 'Critical'
        })
    else:
        monthly_target = round(revenue * 26 * 1.15, 2)
        insights.append({
            'icon': 'fa-rocket',
            'color': '#10b981',
            'bg': 'rgba(16,185,129,0.1)',
            'title': 'Scale Your Revenue Stream',
            'text': f'With a healthy margin of {profit_margin:.1f}%, you are ready to scale. Adding one more peak-hour shift or a home delivery service could help reach ₹{monthly_target:,.0f}/month.',
            'impact': 'Growth Opportunity'
        })

    # Insight 7: Combo / Upsell
    insights.append({
        'icon': 'fa-layer-group',
        'color': '#ec4899',
        'bg': 'rgba(236,72,153,0.1)',
        'title': 'Introduce Combo Offers & Bundles',
        'text': f'Create 2–3 combo packages featuring "{best_item}" alongside complementary products. Combos typically increase the transaction value by 25–40% with minimal extra effort.',
        'impact': 'Medium Impact'
    })

    return insights[:7]


# ─── Business Diagnosis Engine ────────────────────────────────────────────────
def generate_diagnosis(data, profit, profit_margin, revenue_per_customer, expense_ratio, health_score):
    revenue = float(data['revenue'])
    expenses = float(data['expenses'])
    customers = int(data['customers'])
    avg_bill = float(data['avg_bill'])
    best_item = data['best_item']
    business_type = data.get('business_type', 'Business')

    flaws = []

    # ── Flaw 1: High Expense Ratio ────────────────────────────────────────────
    if expense_ratio > 75:
        daily_loss = round(expenses - revenue * 0.65, 2)
        flaws.append({
            'id': 1,
            'risk': 'Critical',
            'risk_color': '#ef4444',
            'risk_bg': 'rgba(239,68,68,0.08)',
            'icon': 'fa-fire',
            'title': 'Dangerously High Expenses',
            'flaw': f'Your expenses are {expense_ratio:.1f}% of your revenue. For every ₹100 earned, you are spending ₹{expense_ratio:.0f} — leaving almost nothing as profit. At this rate, one bad week could put the business at risk.',
            'fix_title': 'Immediate Cost Audit',
            'fix': f'List every daily expense and cut the bottom 15% immediately. Renegotiate your rent or supplier prices. Switching to bulk purchasing for "{best_item}" ingredients alone could save ₹{round(expenses*0.10):,}/month.',
            'impact': f'Saving just 10% on expenses = ₹{round(expenses*0.10*26):,}/month added back to profit.',
            'steps': [
                'List all daily expenses in a notebook this week',
                'Identify top 3 costs and negotiate each one',
                'Switch at least 1 supplier to a cheaper alternative',
                'Track expenses daily using a simple app'
            ]
        })
    elif expense_ratio > 60:
        flaws.append({
            'id': 1,
            'risk': 'High',
            'risk_color': '#f97316',
            'risk_bg': 'rgba(249,115,22,0.08)',
            'icon': 'fa-triangle-exclamation',
            'title': 'Above-Average Expense Ratio',
            'flaw': f'Your expenses consume {expense_ratio:.1f}% of revenue. The healthy benchmark for a {business_type} is below 55–60%. You are overspending by roughly ₹{round((expense_ratio-58)/100*revenue):,} per day.',
            'fix_title': 'Targeted Cost Reduction Plan',
            'fix': f'Focus on your top 2 expense categories. Even a 8% reduction in total costs would save ₹{round(expenses*0.08):,}/day and ₹{round(expenses*0.08*26):,}/month — directly boosting your profit.',
            'impact': f'Reducing expense ratio to 58% would add ₹{round((expense_ratio-58)/100*revenue*26):,} to monthly profit.',
            'steps': [
                'Compare your supplier prices with 2 competitors',
                'Reduce electricity usage during non-peak hours',
                'Review staff scheduling to avoid idle hours',
                'Eliminate any subscription or service not actively used'
            ]
        })

    # ── Flaw 2: Low Profit Margin ─────────────────────────────────────────────
    if profit_margin < 10:
        flaws.append({
            'id': 2,
            'risk': 'Critical',
            'risk_color': '#ef4444',
            'risk_bg': 'rgba(239,68,68,0.08)',
            'icon': 'fa-chart-line',
            'title': 'Critically Low Profit Margin',
            'flaw': f'Your profit margin is only {profit_margin:.1f}%. This means after all expenses, you keep just ₹{profit_margin:.0f} from every ₹100 earned. Industry standard for {business_type} is 20–30%. You are earning less than half of what you should.',
            'fix_title': 'Margin Recovery Strategy',
            'fix': f'Increase prices on your top 5 items by just 8–10%. Customers rarely notice small price increases on popular items. Raising the price of "{best_item}" by ₹10 across {customers} customers = ₹{customers*10:,}/day extra.',
            'impact': f'Reaching a 20% margin would mean ₹{round(revenue*0.20*26):,}/month profit instead of current ₹{round(profit*26):,}.',
            'steps': [
                f'Increase price of "{best_item}" by ₹10–15 immediately',
                'Identify your 3 lowest-margin items and remove or reprice them',
                'Introduce a premium version of your best seller at higher price',
                'Add high-margin add-ons (drinks, sides, accessories) to every sale'
            ]
        })
    elif profit_margin < 20:
        flaws.append({
            'id': 2,
            'risk': 'Medium',
            'risk_color': '#f59e0b',
            'risk_bg': 'rgba(245,158,11,0.08)',
            'icon': 'fa-arrow-trend-down',
            'title': 'Below-Benchmark Profit Margin',
            'flaw': f'At {profit_margin:.1f}% profit margin, you are below the {business_type} industry benchmark of 20–30%. You are working hard but not keeping enough of what you earn. Over a year, this gap costs you ₹{round((0.20-profit_margin/100)*revenue*312):,}.',
            'fix_title': 'Margin Improvement Plan',
            'fix': f'Focus on selling more of your high-margin items. Bundle "{best_item}" with a high-profit side item. Even moving to 20% margin adds ₹{round((0.20 - profit_margin/100)*revenue*26):,} per month.',
            'impact': f'Closing the margin gap to 20% = +₹{round((0.20-profit_margin/100)*revenue*26):,}/month.',
            'steps': [
                'Calculate the margin on each product you sell',
                'Promote the top 3 highest-margin items more visibly',
                'Train staff to upsell premium options',
                'Remove the 2 lowest-selling, low-margin items from menu/stock'
            ]
        })

    # ── Flaw 3: Low Customer Count ────────────────────────────────────────────
    if customers < 30:
        flaws.append({
            'id': 3,
            'risk': 'High',
            'risk_color': '#f97316',
            'risk_bg': 'rgba(249,115,22,0.08)',
            'icon': 'fa-users-slash',
            'title': 'Very Low Customer Footfall',
            'flaw': f'Only {customers} customers per day is critically low for a {business_type}. A comparable business in {data["city"]} typically serves 60–100+ customers daily. You are potentially missing ₹{round((60-customers)*avg_bill*26):,}/month in revenue.',
            'fix_title': 'Customer Acquisition Campaign',
            'fix': f'Run a "Bring a Friend" offer this week — any customer who brings a new person gets 10% off. Post daily on WhatsApp Status with photos of "{best_item}". Put a standee or board outside your shop with today\'s special.',
            'impact': f'Adding just 20 more daily customers at ₹{avg_bill:.0f} avg bill = ₹{round(20*avg_bill*26):,}/month more revenue.',
            'steps': [
                'Put a attractive board/banner outside your shop today',
                'Start a WhatsApp broadcast list of existing customers',
                'Offer a first-visit discount to every new customer this week',
                'Ask every satisfied customer to bring one friend'
            ]
        })
    elif customers < 60:
        flaws.append({
            'id': 3,
            'risk': 'Medium',
            'risk_color': '#f59e0b',
            'risk_bg': 'rgba(245,158,11,0.08)',
            'icon': 'fa-users',
            'title': 'Customer Footfall Can Be Higher',
            'flaw': f'With {customers} customers/day, there is significant growth potential. Most successful {business_type} businesses in {data["city"]} see 80–120 customers daily. You could be doing ₹{round((80-customers)*avg_bill*26):,} more per month.',
            'fix_title': 'Footfall Growth Strategy',
            'fix': f'Create a Google Business Profile for free — 60% of customers search online before visiting. Share "{best_item}" photos on Instagram/Facebook. Happy customers are your best marketing — start asking for Google reviews.',
            'impact': f'Growing to 80 customers/day = ₹{round((80-customers)*avg_bill*26):,} additional monthly revenue.',
            'steps': [
                'Create a free Google Business Profile this week',
                'Take 3 photos of your best products and post on social media',
                'Ask 5 happy customers for a Google review today',
                'Display a "Customer of the Day" board to create engagement'
            ]
        })

    # ── Flaw 4: No Digital Presence / Low Tech ───────────────────────────────
    flaws.append({
        'id': 4,
        'risk': 'Medium',
        'risk_color': '#f59e0b',
        'risk_bg': 'rgba(245,158,11,0.08)',
        'icon': 'fa-wifi',
        'title': 'Zero Digital Tracking & No Online Presence',
        'flaw': f'{data["business_name"]} is currently running 100% on memory and guesswork. You have no way to know which day was your best, which item is most profitable, or whether your revenue is growing or shrinking month over month. This is the #1 reason small businesses plateau.',
        'fix_title': 'Digital Transformation (Simple & Low Cost)',
        'fix': f'Start with just 3 things: (1) A free Google Business Profile so customers can find you online. (2) A WhatsApp Business account to send offers to regular customers. (3) A simple daily record of revenue and expenses — exactly what BusinessPulse does for you automatically.',
        'impact': 'Businesses with digital tracking grow 2–3x faster because they make data-driven decisions instead of guesses.',
        'steps': [
            'Set up Google Business Profile (free, takes 15 minutes)',
            'Create WhatsApp Business account and add your product catalogue',
            'Use BusinessPulse to track daily revenue, expenses and customers',
            'Review your weekly dashboard every Monday morning'
        ]
    })

    # ── Flaw 5: Revenue Concentration Risk ───────────────────────────────────
    flaws.append({
        'id': 5,
        'risk': 'Low',
        'risk_color': '#3b82f6',
        'risk_bg': 'rgba(59,130,246,0.08)',
        'icon': 'fa-egg',
        'title': f'Over-Reliance on One Product: "{best_item}"',
        'flaw': f'Your business depends heavily on "{best_item}" as the top seller. If this item faces a supply issue, price increase, or a competitor starts selling it cheaper — your entire revenue is at risk. Businesses with only 1–2 strong products are fragile.',
        'fix_title': 'Product Diversification Plan',
        'fix': f'Introduce 2 new complementary products this month. If "{best_item}" earns well, create a premium version at 30% higher price and a budget version to capture more customer segments. Cross-sell at least 1 add-on with every order.',
        'impact': f'Adding 2 new products that each sell 15 units/day at ₹{round(avg_bill*0.6):,} each = ₹{round(2*15*avg_bill*0.6*26):,}/month extra.',
        'steps': [
            f'Research 2 products that complement "{best_item}"',
            'Test them with a small stock investment first',
            'Create a "Combo Deal" pairing best seller with new item',
            'Track which new items sell best and expand those'
        ]
    })

    # ── Flaw 6: No Repeat Customer System ────────────────────────────────────
    repeat_potential = round(customers * 0.3 * avg_bill * 26, 2)
    flaws.append({
        'id': 6,
        'risk': 'Medium',
        'risk_color': '#f59e0b',
        'risk_bg': 'rgba(245,158,11,0.08)',
        'icon': 'fa-rotate',
        'title': 'No System to Bring Customers Back',
        'flaw': f'Every day you serve {customers} customers — but do you know how many come back tomorrow? Most small businesses lose 60–70% of customers after the first visit simply because there is no reason given to return. This silent loss costs you ₹{repeat_potential:,.0f}/month.',
        'fix_title': 'Customer Retention System',
        'fix': f'Start a simple punch card loyalty program today — "Buy 5, Get 1 Free". Collect customer WhatsApp numbers and send a monthly special offer. Even getting 30% of customers to return doubles your effective customer base without any advertising cost.',
        'impact': f'Converting 30% of daily customers into repeat visitors = ₹{repeat_potential:,.0f}/month in guaranteed recurring revenue.',
        'steps': [
            'Print 50 simple loyalty punch cards this week (cost: ₹100)',
            'Collect WhatsApp numbers from every customer',
            'Send a special offer every 2 weeks to your customer list',
            'Greet returning customers by name — personal touch creates loyalty'
        ]
    })

    return flaws


# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_dashboard():
    data = request.get_json()

    # Validate required fields
    required = ['business_name', 'owner_name', 'business_type', 'city',
                'revenue', 'expenses', 'customers', 'avg_bill', 'best_item']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" is required'}), 400

    try:
        # Save to DB
        entry = BusinessEntry(
            business_name=data['business_name'],
            owner_name=data['owner_name'],
            business_type=data['business_type'],
            city=data['city'],
            revenue=float(data['revenue']),
            expenses=float(data['expenses']),
            customers=int(data['customers']),
            avg_bill=float(data['avg_bill']),
            best_item=data['best_item']
        )
        db.session.add(entry)
        db.session.commit()

        analytics = calculate_analytics(data)
        return jsonify({'success': True, 'data': analytics})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/history')
def history():
    entries = BusinessEntry.query.order_by(BusinessEntry.created_at.desc()).limit(50).all()
    return jsonify([e.to_dict() for e in entries])


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'version': '1.0.0', 'product': 'BusinessPulse'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
