# Sales Target & Dashboard Feature Guide

## Overview

The Sales Target & Dashboard feature allows individual salespeople to track their monthly sales targets and monitor their progress in real-time. This feature includes:

- **Monthly Sales Targets**: Set individual sales targets for each salesperson per month
- **Progress Tracking**: Real-time calculation of achieved sales vs. target
- **Performance Dashboard**: Comprehensive dashboard showing remaining target, days left in month, and daily average needed
- **Performance Metrics**: Calculate if salesperson is on track to meet their target

## Database Schema

### SalesTarget Table

```sql
CREATE TABLE sales_target (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_person VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    target_amount FLOAT NOT NULL,
    assignment_type VARCHAR(50) DEFAULT 'manual',
    assigned_by VARCHAR(100),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_sales_target (sales_person, year, month)
);
```

**Key Constraints:**
- Unique constraint on `(sales_person, year, month)` to prevent duplicate targets
- Each salesperson can have only one target per month

## API Endpoints

### 1. Get Salesperson Dashboard

**Endpoint:** `GET /api/sales/dashboard`

**Parameters:**
- `salesPerson` (required): Name of the salesperson
- `year` (optional): Year (defaults to current year)
- `month` (optional): Month 1-12 (defaults to current month)

**Response:**
```json
{
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "monthName": "December",
  "target": {
    "amount": 100000,
    "details": {
      "id": 1,
      "salesPerson": "John Doe",
      "year": 2024,
      "month": 12,
      "targetAmount": 100000,
      "assignmentType": "manual",
      "assignedBy": "admin",
      "notes": "December target",
      "createdAt": "2024-01-15T10:30:00",
      "updatedAt": "2024-01-15T10:30:00"
    }
  },
  "achieved": {
    "amount": 75000.50,
    "percentage": 75.0
  },
  "remaining": {
    "amount": 24999.50,
    "percentage": 25.0
  },
  "exceeded": 0,
  "daysMetrics": {
    "daysInMonth": 31,
    "daysElapsed": 15,
    "daysRemaining": 16,
    "isCurrentMonth": true
  },
  "dailyAverage": {
    "needed": 1562.47,
    "achieved": 5000.03,
    "onTrack": true
  },
  "status": "progressing"
}
```

**Status Meanings:**
- `on_track`: Achieved >= 100% of target
- `progressing`: Achieved between 50-100% of target
- `at_risk`: Achieved < 50% of target

### 2. Set Sales Target

**Endpoint:** `POST /api/sales/targets`

**Request Body:**
```json
{
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "targetAmount": 100000,
  "assignedBy": "admin",
  "notes": "Monthly sales target"
}
```

**Response:**
```json
{
  "id": 1,
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "targetAmount": 100000,
  "assignmentType": "manual",
  "assignedBy": "admin",
  "notes": "Monthly sales target",
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

### 3. Get Current Month Target

**Endpoint:** `GET /api/sales/targets/current`

**Parameters:**
- `salesPerson` (required): Name of the salesperson

**Response:**
```json
{
  "id": 1,
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "targetAmount": 100000,
  "assignmentType": "manual",
  "assignedBy": "admin",
  "notes": "Monthly sales target",
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

### 4. Get All Targets for Salesperson

**Endpoint:** `GET /api/sales/targets/all`

**Parameters:**
- `salesPerson` (required): Name of the salesperson
- `year` (optional): Year (defaults to current year)

**Response:**
```json
{
  "targets": [
    {
      "id": 1,
      "salesPerson": "John Doe",
      "year": 2024,
      "month": 1,
      "targetAmount": 50000,
      "assignmentType": "manual",
      "assignedBy": "admin",
      "notes": "January target",
      "createdAt": "2024-01-15T10:30:00",
      "updatedAt": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "salesPerson": "John Doe",
      "year": 2024,
      "month": 2,
      "targetAmount": 55000,
      "assignmentType": "manual",
      "assignedBy": "admin",
      "notes": "February target",
      "createdAt": "2024-01-15T10:30:00",
      "updatedAt": "2024-01-15T10:30:00"
    }
  ],
  "count": 2
}
```

### 5. Get Performance Metrics

**Endpoint:** `GET /api/sales/performance`

**Parameters:**
- `salesPerson` (required): Name of the salesperson
- `year` (required): Year
- `month` (required): Month 1-12

**Response:**
```json
{
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "achievedSales": 75000.50,
  "target": {
    "id": 1,
    "salesPerson": "John Doe",
    "year": 2024,
    "month": 12,
    "targetAmount": 100000,
    "assignmentType": "manual",
    "assignedBy": "admin",
    "notes": "December target",
    "createdAt": "2024-01-15T10:30:00",
    "updatedAt": "2024-01-15T10:30:00"
  },
  "achievedPercentage": 75.0
}
```

## Setup Instructions

### 1. Create the Migration

Run the migration script to create the `sales_target` table:

```bash
python run_sales_target_migration.py
```

### 2. Update Models

The `SalesTarget` model has been added to `models/sales.py`. The model is automatically imported in the Flask app.

### 3. Initialize Flask

Make sure to import the new model in your app initialization:

```python
from models.sales import SalesTarget
```

## Usage Examples

### Example 1: Set Monthly Target for a Salesperson

```python
# Using the API
POST /api/sales/targets
{
  "salesPerson": "John Doe",
  "year": 2024,
  "month": 12,
  "targetAmount": 500000,
  "assignedBy": "admin",
  "notes": "Q4 aggressive sales target"
}
```

### Example 2: Get Dashboard for Current Month

```python
# Using the API
GET /api/sales/dashboard?salesPerson=John Doe

# Returns full dashboard with all metrics
```

### Example 3: Track Performance During Month

```python
# Using the API
GET /api/sales/performance?salesPerson=John Doe&year=2024&month=12

# Returns current achieved vs target
```

### Example 4: Compare Target vs Actual

The dashboard response includes:

```
Target Amount: ₹500,000
Achieved So Far: ₹375,000 (75%)
Remaining Target: ₹125,000 (25%)
Days in Month: 31
Days Elapsed: 15
Days Remaining: 16
Daily Average Needed: ₹7,812.50
Daily Average Achieved: ₹25,000
Status: PROGRESSING (On track to exceed target)
```

## Key Features

### 1. **Real-time Calculation**
- Achievement calculated from actual sales orders created in the month
- Excludes cancelled orders from calculation
- Updates automatically as new orders are created

### 2. **Progress Tracking**
- Visual percentage of target achieved
- Remaining target amount
- Days remaining in month

### 3. **Performance Analysis**
- Daily average sales achieved
- Daily average needed to hit target
- On-track indicator
- Status classification (on_track, progressing, at_risk)

### 4. **Flexibility**
- Can set targets manually by admin
- Supports future targets (planning)
- Supports past targets (historical tracking)
- Unique constraint prevents duplicate targets

### 5. **Month Handling**
- Automatically calculates current month if not specified
- Handles edge cases (future months, past months)
- Calculates exact days remaining

## Business Logic

### Achievement Calculation

```
Achieved Sales = SUM(final_amount) of all non-cancelled orders 
                 created in the month by the salesperson
```

### Remaining Target

```
Remaining = MAX(Target - Achieved, 0)
```

### Daily Average Needed

```
Daily Average Needed = Remaining / Days Remaining
```

### Progress Percentage

```
Progress % = (Achieved / Target) * 100
```

### Status Determination

```
if Progress % >= 100: status = "on_track"
elif Progress % >= 50: status = "progressing"
else: status = "at_risk"
```

## Dashboard Metrics Explained

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Target Amount** | Monthly sales target in rupees | Overall goal for the month |
| **Achieved Amount** | Actual sales completed to date | Track progress |
| **Achieved %** | Percentage of target achieved | Quick performance check |
| **Remaining Amount** | Amount still needed to hit target | Motivational metric |
| **Days Remaining** | Working days left in month | Planning scope |
| **Daily Avg Needed** | Average daily sales needed to hit target | Performance requirement |
| **Daily Avg Achieved** | Average daily sales so far | Current productivity |
| **On Track** | Boolean - if daily avg achieved >= daily avg needed | Quick status check |
| **Status** | on_track / progressing / at_risk | Overall performance level |

## Integration with Sales Orders

When a sales order is created, the following happens:
1. Order is recorded with the salesperson's name
2. Final amount is tracked
3. Dashboard automatically reflects in achieved sales
4. Progress percentage updates in real-time
5. Status classification updates based on new progress

## Frontend Implementation (React/Vue)

### Component Structure

```
SalesPersonalDashboard
├── TargetCard
│   ├── Target Amount
│   ├── Achieved Amount
│   ├── Progress Bar
│   └── Status Badge
├── MetricsGrid
│   ├── Remaining Target Card
│   ├── Days Remaining Card
│   ├── Daily Average Card
│   └── Performance Status Card
└── ChartsSection
    ├── Progress Over Month
    └── Daily Achievement Trend
```

### Key Data Points to Display

1. **Progress Bar**: Animated bar showing % progress
2. **Remaining Badge**: Show remaining amount and %
3. **Days Counter**: Days elapsed / Total days
4. **Daily Average**: Comparison of needed vs achieved
5. **Status Indicator**: Color-coded status

## Considerations

### 1. **Salesperson Identification**
- Currently uses `sales_person` string field from SalesOrder
- Ensure consistent naming when setting targets
- Consider linking to User model in future

### 2. **Time Zone**
- All calculations use UTC (utcnow())
- Adjust if business operates in different timezone

### 3. **Order Status Exclusion**
- Cancelled orders are excluded from achievement calculation
- Consider excluding other statuses as needed

### 4. **Year/Month Validation**
- Month must be 1-12
- Year validation recommended for future dates

## Future Enhancements

1. **Link to User Model**: Link SalesTarget to User instead of string
2. **Team Targets**: Set targets for teams in addition to individuals
3. **Automated Target Calculation**: Formula-based targets from historical data
4. **Incentive Integration**: Connect targets to commission/bonus calculation
5. **Notifications**: Alert salespeople when at risk
6. **Historical Trends**: Show multi-year performance
7. **Territory-based Targets**: Different targets by sales territory
8. **Commission Calculator**: Auto-calculate commission based on target achievement

## Troubleshooting

### Issue: Dashboard shows 0% progress

**Cause:** No sales orders found for the salesperson in the month

**Solution:**
1. Check if orders are created under the correct salesperson name
2. Verify order status is not 'cancelled'
3. Check if orders are created in the correct month/year

### Issue: Target not found error

**Cause:** No target set for the salesperson/month combination

**Solution:**
1. Set target using POST /api/sales/targets
2. Ensure salesPerson name matches exactly

### Issue: Inconsistent daily average calculations

**Cause:** Time zone differences or wrong month selected

**Solution:**
1. Verify year and month parameters
2. Check server timezone settings

## Support

For issues or questions about the Sales Target feature, refer to the technical documentation or contact the development team.