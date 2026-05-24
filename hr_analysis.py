
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

np.random.seed(99)
N = 10000


# 1. GENERATE EMPLOYEE DATASET

departments  = ['Engineering', 'Sales', 'HR', 'Finance', 'Marketing', 'Operations']
leave_types  = ['Sick', 'Casual', 'Earned', 'Maternity/Paternity', 'Unpaid']
statuses     = ['Active', 'Resigned', 'On Leave']
genders      = ['Male', 'Female']

employee_ids = [f"EMP{str(i).zfill(4)}" for i in range(1, N + 1)]

df = pd.DataFrame({
    'employee_id'   : employee_ids,
    'department'    : np.random.choice(departments, N, p=[0.30, 0.20, 0.10, 0.15, 0.15, 0.10]),
    'gender'        : np.random.choice(genders, N, p=[0.55, 0.45]),
    'age'           : np.random.randint(22, 58, N),
    'experience_yrs': np.random.randint(0, 30, N),
    'salary'        : np.random.normal(60000, 20000, N).clip(25000, 150000).round(-2),
    'attendance_pct': np.random.normal(88, 10, N).clip(40, 100).round(1),
    'leave_days'    : np.random.poisson(lam=9, size=N),
    'leave_type'    : np.random.choice(leave_types, N, p=[0.30, 0.25, 0.25, 0.10, 0.10]),
    'performance'   : np.random.choice(['Excellent', 'Good', 'Average', 'Poor'], N,
                                        p=[0.20, 0.40, 0.30, 0.10]),
    'status'        : np.random.choice(statuses, N, p=[0.80, 0.12, 0.08]),
    'work_mode'     : np.random.choice(['On-site', 'Remote', 'Hybrid'], N, p=[0.40, 0.25, 0.35]),
    'join_date'     : pd.to_datetime(
                        np.random.choice(pd.date_range('2015-01-01', '2023-12-31'), N)
                      ),
    'overtime_hrs'  : np.random.poisson(lam=5, size=N),
    # Intentional dirty data
    'email'         : [f"emp{i}@company.com" if i % 20 != 0 else None for i in range(N)],
    'manager_id'    : [f"EMP{np.random.randint(1, 200):04d}" if i % 15 != 0 else np.nan
                       for i in range(N)],
})


# 2. DATA CLEANING

print("=" * 55)
print("       HR ANALYTICS — DATA CLEANING REPORT")
print("=" * 55)
print(f"\n📋 Raw records : {len(df):,}")
print(f"   Missing emails    : {df['email'].isnull().sum()}")
print(f"   Missing manager   : {df['manager_id'].isnull().sum()}")
print(f"   Duplicate emp IDs : {df['employee_id'].duplicated().sum()}")

# Fill missing emails
df['email'] = df['email'].fillna(
    df['employee_id'].str.lower() + '@company.com'
)
# Fill missing managers with placeholder
df['manager_id'] = df['manager_id'].fillna('EMP0001')

# Derived columns
df['tenure_years']    = ((pd.Timestamp.now() - df['join_date']).dt.days / 365).round(1)
df['is_senior']       = df['experience_yrs'] >= 10
df['productivity_score'] = (
    df['attendance_pct'] * 0.5 +
    df['performance'].map({'Excellent': 40, 'Good': 30, 'Average': 20, 'Poor': 10}) * 0.3 +
    (100 - df['leave_days'].clip(0, 30) * 2) * 0.2
).round(1)

print(f"\n✅ After cleaning: {len(df):,} records — 0 missing values")


# 3. KPI SUMMARY

print("\n── KEY HR KPIs ───────────────────────────────────────")
active = df[df['status'] == 'Active']
print(f"   Total Employees    : {len(df):,}")
print(f"   Active Employees   : {len(active):,} ({len(active)/len(df)*100:.1f}%)")
print(f"   Avg Attendance     : {df['attendance_pct'].mean():.1f}%")
print(f"   Avg Leave Days     : {df['leave_days'].mean():.1f} days/employee")
print(f"   Avg Salary         : ₹{df['salary'].mean():,.0f}")
print(f"   Avg Productivity   : {df['productivity_score'].mean():.1f}/100")
print(f"   Attrition Rate     : {(df['status']=='Resigned').sum()/len(df)*100:.1f}%")

print("\n── DEPARTMENT SUMMARY ────────────────────────────────")
dept_summary = df.groupby('department').agg(
    headcount     = ('employee_id', 'count'),
    avg_salary    = ('salary', 'mean'),
    avg_attendance= ('attendance_pct', 'mean'),
    avg_leave     = ('leave_days', 'mean'),
    avg_prod      = ('productivity_score', 'mean')
).round(1)
print(dept_summary.to_string())


# 4. VISUALIZATIONS

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("HR Analytics Dashboard — Praveena", fontsize=16,
             fontweight='bold', y=0.98)
colors = sns.color_palette("tab10")

# 4a. Department Headcount
hc = df['department'].value_counts()
axes[0, 0].bar(hc.index, hc.values, color=colors)
axes[0, 0].set_title("Headcount by Department")
axes[0, 0].set_ylabel("Employees")
axes[0, 0].tick_params(axis='x', rotation=20)
for i, v in enumerate(hc.values):
    axes[0, 0].text(i, v + 30, str(v), ha='center', fontsize=8)

# 4b. Attendance Distribution
axes[0, 1].hist(df['attendance_pct'], bins=30, color='steelblue',
                edgecolor='white', alpha=0.85)
axes[0, 1].axvline(df['attendance_pct'].mean(), color='red',
                   linestyle='--', linewidth=1.5, label=f"Mean: {df['attendance_pct'].mean():.1f}%")
axes[0, 1].set_title("Attendance % Distribution")
axes[0, 1].set_xlabel("Attendance %"); axes[0, 1].set_ylabel("Frequency")
axes[0, 1].legend()

# 4c. Leave Type Breakdown
lt = df['leave_type'].value_counts()
axes[0, 2].pie(lt, labels=lt.index, autopct='%1.1f%%',
               startangle=140, colors=sns.color_palette("Set3", len(lt)))
axes[0, 2].set_title("Leave Type Breakdown")

# 4d. Salary by Department (Boxplot)
dept_order = df.groupby('department')['salary'].median().sort_values().index
sns.boxplot(data=df, x='department', y='salary', order=dept_order,
            ax=axes[1, 0], palette="pastel", showfliers=False)
axes[1, 0].set_title("Salary Distribution by Department")
axes[1, 0].set_xticklabels(dept_order, rotation=20, fontsize=8)
axes[1, 0].set_ylabel("Salary (₹)")

# 4e. Performance Distribution
perf_order = ['Excellent', 'Good', 'Average', 'Poor']
perf_counts = df['performance'].value_counts().reindex(perf_order)
palette = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
axes[1, 1].bar(perf_counts.index, perf_counts.values, color=palette)
axes[1, 1].set_title("Employee Performance Distribution")
axes[1, 1].set_ylabel("Count")
for i, v in enumerate(perf_counts.values):
    axes[1, 1].text(i, v + 50, str(v), ha='center', fontsize=9)

# 4f. Productivity Score Heatmap (Dept × Work Mode)
pivot = df.groupby(['department', 'work_mode'])['productivity_score'].mean().unstack()
sns.heatmap(pivot, ax=axes[1, 2], annot=True, fmt='.1f',
            cmap='RdYlGn', linewidths=0.5,
            cbar_kws={'label': 'Productivity Score'})
axes[1, 2].set_title("Avg Productivity: Dept × Work Mode")
axes[1, 2].set_xlabel("Work Mode"); axes[1, 2].set_ylabel("")
axes[1, 2].tick_params(axis='y', rotation=0)

plt.tight_layout()
plt.savefig("hr_dashboard.png", dpi=150, bbox_inches='tight')
print("\n✅ Dashboard saved → hr_dashboard.png")
plt.show()

print("\n" + "=" * 55)
print("  HR Analysis complete!")
print("=" * 55)
