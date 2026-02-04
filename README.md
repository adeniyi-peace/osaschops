# 🥡 Osaschops - Vendor Management & Food Ordering System

**Osaschops** is a full-featured Django e-commerce platform designed for food vendors. It bridges the gap between a seamless customer ordering experience and a powerful kitchen management dashboard.

Unlike standard e-commerce templates, this project focuses on **real-world operational workflows**, including End-of-Day financial reporting, kitchen display systems, and robust payment verification.

---

## 📸 Screenshots

| Vendor Dashboard | EOD Report |
|:---:|:---:|
| ![Vendor Dashboard](path/to/dashboard-screenshot.png) | ![EOD Report](path/to/report-screenshot.png) |
| *Real-time revenue & order tracking* | *Print-ready daily financial summary* |

---

## ✨ Key Features

### 👨‍🍳 For Vendors (Kitchen Side)
- **Live Dashboard:** Real-time metrics for "Today's Revenue," "Active Orders," and "Kitchen Efficiency."
- **EOD Reporting:** One-click generation of printable **End-of-Day Reports** summarizing cash vs. digital sales and inventory usage.
- **Sales Analytics:** Interactive charts (Chart.js) to visualize revenue trends, delivery zone performance, and top-selling items over custom date ranges.
- **Kitchen Display System (KDS):** Digital ticket management to track order status from *Prep* to *Ready* to *Delivered*.

### 🛒 For Customers (Client Side)
- **AJAX Cart:** Seamless "Add to Cart" experience with dynamic category filtering and instant UI updates.
- **Smart Checkout:** Supports **Paystack** (Card/Transfer) and **Pay on Delivery**.
- **Order Tracking:** Real-time updates on order status.

### ⚙️ Technical Highlights
- **"Ghost Order" Handling:** Intelligent logic to filter out abandoned payment sessions without losing data analytics potential.
- **Atomic Transactions:** Ensures database integrity during checkout (orders are only created if line items are successfully saved).
- **Printer-Friendly CSS:** Specialized styling for generating physical receipts and reports directly from the browser.

---

## 🛠️ Tech Stack

- **Backend:** Python, Django (Class-Based Views, Mixins)
- **Frontend:** Django Templates, Tailwind CSS, JavaScript (AJAX, Chart.js)
- **Database:** PostgreSQL (Production) / SQLite (Dev)
- **Payments:** Paystack API Integration
- **Utilities:** `django-humanize`, `requests`

---

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/adeniyi-peace/osaschops.git](https://github.com/adeniyi-peace/osaschops.git)
   cd osaschops

2. **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Environment Variables Create a .env file in the root directory and add your keys:**
    ```Code snippet
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    PAYSTACK_SECRET_KEY=your_paystack_secret_key
    PAYSTACK_PUBLIC_KEY=your_paystack_public_key
    ```

5. **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate

6. **Create a Superuser (to access the admin panel)**
    ```bash
    python manage.py createsuperuser

7. **Critical Step: Configure Store Profile To avoid a 500 Server Error, you must initialize the store settings:**
    - Run the server: python manage.py runserver
    - Log in to the Admin panel at http://127.0.0.1:8000/admin
    - Navigate to the Store Profile (or Vendor) tab.
    - Create exactly one instance of the vendor profile.
    - **Note**: Do not change the default name; the system requires exactly one instance to function correctly.

8. **Run the Server**
    ```bash
    python manage.py runserver
    Visit http://127.0.0.1:8000 in your browser.

9. **Manage Categories**
    Products are organized by categories. Currently, Categories can only be created or edited via the Django Admin panel.


## Key Workflows Explained
- **The "Ghost Order" Solution**
    To prevent database clutter from abandoned Paystack transactions, the system uses a dual-check approach:

    Soft Filtering: Unpaid orders are preserved in the database for analytics (e.g., "Abandoned Cart" reports) but filtered out of the Kitchen Dashboard using custom Q object queries.

- **Session Cleanup**: If a user returns to checkout after a failed attempt, the previous unpaid session is cleared automatically to prevent duplicates.

- **EOD Report Generation**
    The EODReportView aggregates data from the Order, OrderItem, and Payment models. It uses a specialized print template (media print CSS) to strip away navigation bars and buttons, producing a clean, professional invoice format for physical printing.

Developed with ❤️ by Adeniyi Peace