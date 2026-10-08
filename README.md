<a href="https://github.com/maaarwa4">
  <img width="100%" src="assets/banner.svg" alt="CarRental" />
</a>

<div align="center">

<a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
<a href="https://flask.palletsprojects.com"><img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" /></a>
<a href="https://www.mongodb.com"><img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" /></a>
<a href="https://jinja.palletsprojects.com"><img src="https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2" /></a>

</div>

<br>

<h2><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Light%20Bulb.png" width="32" align="center" />&nbsp; Overview</h2>

CarRental centralizes the operations of a car rental agency: **fleet**, **customers** and **bookings**.
The application relies on **role-based access control**: each user only sees the features relevant to their role.

<br>

<h2><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" width="32" align="center" />&nbsp; Features by Role</h2>

<table>
<tr>
<td width="50%" valign="top">

**Administrator**

- Dashboard with key indicators (managers, customers…)
- Create, update and delete **manager accounts**

</td>
<td width="50%" valign="top">

**Manager**

- **Fleet**: add, edit and remove vehicles (with photos)
- **Customers**: manage their own customer portfolio
- **Bookings**: create, edit, accept or decline
- Personal dashboard

</td>
</tr>
</table>

<br>

<h2><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Briefcase.png" width="32" align="center" />&nbsp; Business Rules</h2>

- A booking can only be made on an **available** vehicle
- **Overlap control**: a vehicle cannot be booked twice for the same period
- Booking lifecycle: **pending → confirmed / cancelled**
- Vehicle availability is **updated automatically** with each booking
- User email addresses are **unique**

```
PENDING  ──►  CONFIRMED
   │
   └──────►  CANCELLED
```

<br>

<h2><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Laptop.png" width="32" align="center" />&nbsp; Security & Tech Stack</h2>

- Passwords **hashed with bcrypt**
- Flask sessions with **role checks on every route**
- Secure image uploads (`secure_filename`)
- Sensitive configuration kept in **environment variables**

| Layer | Technology |
|:---|:---|
| Backend | Python · Flask |
| Database | MongoDB (PyMongo) |
| Frontend | Jinja2 templates · HTML · CSS |
| Security | bcrypt · Werkzeug |
| Notifications | Flask-Mail |

```
CarRental/
├── app.py            # Flask application: routes and business logic
├── crypt.py          # Admin account creation script
├── requirements.txt  # Python dependencies
├── .env.example      # Configuration template
├── templates/        # Jinja2 views (dashboards, forms, lists)
└── static/
    ├── images/       # Visual assets
    └── uploads/      # Vehicle photos
```

<br>

<h2><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Hammer%20and%20Wrench.png" width="32" align="center" />&nbsp; Getting Started</h2>

**Prerequisites:** Python 3.8+ and a local MongoDB instance (`mongodb://localhost:27017`)

```bash
# 1. Clone the repository
git clone https://github.com/maaarwa4/CarRental.git
cd CarRental

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the environment
cp .env.example .env    # then fill in the values

# 4. Create the admin account
python crypt.py

# 5. Run the app
python app.py
```

<br>

<div align="center">

Built by **Marwa Bounoua**

<a href="https://linkedin.com/in/marwa-bounoua-877300263"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="https://github.com/maaarwa4"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" /></a>

</div>

<a href="https://github.com/maaarwa4">
  <img width="100%" src="assets/footer.svg" alt="" />
</a>
