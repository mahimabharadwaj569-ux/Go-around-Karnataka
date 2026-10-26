from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from datetime import date, datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key-before-deployment"
DB_PATH = Path(__file__).with_name("trip_companion.db")

# Curated starter guide. Confirm local timings, access rules, and stay details before real travel.
DISTRICTS = [
 {"name":"Bagalkote","landmark":"Badami Cave Temples","places":[("Badami Cave Temples","Rock-cut cave shrines with Chalukyan art."),("Pattadakal","UNESCO-listed group of early Chalukya temples."),("Aihole","Historic temple complex often called a cradle of temple architecture."),("Banashankari Temple","Important temple near Badami."),("Kudalasangama","Pilgrimage site at the meeting of rivers.")],"stays":["Badami town hotels","Homestays around Badami"]},
 {"name":"Ballari","landmark":"Ballari Fort","places":[("Ballari Fort","Hilltop fort with broad views; climb only in safe conditions."),("Kumaraswamy Temple, Sandur","Temple in the Sandur hills."),("Toranagallu region","Gateway area for the Vijayanagara-Hampi circuit."),("Daroji Sloth Bear Sanctuary","Wildlife reserve near the Hampi region; follow forest rules.")],"stays":["Ballari city hotels","Hospitals/transport-accessible business hotels"]},
 {"name":"Belagavi","landmark":"Belagavi Fort","places":[("Belagavi Fort","Historic fort area in the city."),("Kamal Basti","Jain temple known for detailed architecture."),("Gokak Falls","Waterfall and bridge viewpoint; seasonal flow varies."),("Savadatti Yellamma Temple","Major pilgrimage destination."),("Kittur Fort and Palace","Site associated with Kittur Rani Chennamma.")],"stays":["Belagavi city hotels","Gokak/Savadatti town lodges"]},
 {"name":"Bengaluru Rural","landmark":"Devanahalli Fort","places":[("Devanahalli Fort","Historic fort near Devanahalli town."),("Ghati Subramanya Temple","Popular Subramanya temple."),("Nandi Hills","Hilltop sunrise destination near the district boundary; verify route and access."),("Vijayapura town heritage area","Local markets and historic town sights.")],"stays":["Devanahalli hotels","Doddaballapur town stays"]},
 {"name":"Bengaluru Urban","landmark":"Vidhana Soudha","places":[("Vidhana Soudha","Iconic state legislature building; exterior viewing only where permitted."),("Lalbagh Botanical Garden","Historic botanical garden."),("Cubbon Park","Green public park in central Bengaluru."),("Bengaluru Palace","Palace architecture and exhibitions; check visiting hours."),("ISKCON Bengaluru","Large Krishna temple complex."),("Commercial Street","Popular shopping district.")],"stays":["MG Road and central Bengaluru hotels","Indiranagar boutique stays","Budget hostels near transit"]},
 {"name":"Bidar","landmark":"Bidar Fort","places":[("Bidar Fort","Vast fort complex with historic gateways."),("Bahmani Tombs","Historic royal tombs."),("Mahmud Gawan Madrasa","Distinctive medieval learning complex."),("Nanak Jhira Sahib","Important Sikh pilgrimage site."),("Papnash Shiva Temple","Temple associated with local traditions.")],"stays":["Bidar town hotels","Gurudwara-area guesthouses where available"]},
 {"name":"Chamarajanagar","landmark":"Biligiri Ranganatha Swamy Temple (BR Hills)","places":[("BR Hills","Forest hills and temple landscape; follow wildlife rules."),("Biligiri Ranganatha Swamy Temple","Hilltop temple; check access and timings."),("Bandipur Tiger Reserve","Wildlife safari zone; book only through official channels."),("Gopalaswamy Betta","Scenic hill and temple; access may be restricted."),("Barachukki Falls","Waterfall in the wider Shivanasamudra region.")],"stays":["Yelandur/Chamarajanagar town hotels","Authorised forest lodges when available"]},
 {"name":"Chikkaballapur","landmark":"Nandi Hills","places":[("Nandi Hills","Popular hill viewpoint; sunrise access rules may change."),("Bhoga Nandeeshwara Temple","Historic temple complex at the foot of Nandi Hills."),("Skandagiri","Trek destination; use permitted guided/official access."),("Kaiwara","Town associated with saint-poet traditions."),("Jaramadagu Falls","Seasonal nature spot; check local access.")],"stays":["Chikkaballapur town hotels","Nandi Hills-area resorts"]},
 {"name":"Chikkamagaluru","landmark":"Mullayanagiri","places":[("Mullayanagiri","One of Karnataka's best-known high peaks."),("Baba Budangiri","Mountain range and pilgrimage area."),("Hebbe Falls","Forest waterfall; access arrangements can vary."),("Hirekolale Lake","Scenic lake near Chikkamagaluru."),("Belur and Halebidu day trip","Hoysala temple architecture in neighbouring Hassan district.")],"stays":["Chikkamagaluru town hotels","Coffee-estate homestays","Approved resorts on hill routes"]},
 {"name":"Chitradurga","landmark":"Chitradurga Fort","places":[("Chitradurga Fort","Massive hill fort with gateways and ramparts."),("Vani Vilas Sagar Dam","Historic reservoir and viewpoints."),("Chandravalli","Archaeological area and lake."),("Hiriyur Teru Malleshwara Temple","Historic temple in Hiriyur.")],"stays":["Chitradurga town hotels","Hiriyur highway hotels"]},
 {"name":"Dakshina Kannada","landmark":"Kudroli Gokarnath Temple","places":[("Kudroli Gokarnath Temple","Colourful temple complex in Mangaluru."),("Mangaladevi Temple","Historic temple linked to the city's name."),("Panambur Beach","Popular beach; swim only where lifeguards permit."),("Kateel Durga Parameshwari Temple","Major temple on the Nandini River."),("Dharmasthala","Renowned pilgrimage centre."),("Kukke Subramanya","Major temple in the Western Ghats foothills.")],"stays":["Mangaluru city hotels","Udupi/Dharmasthala-area stays","Beachside stays with verified safety standards"]},
 {"name":"Davanagere","landmark":"Santhebennur Pushkarani","places":[("Santhebennur Pushkarani","Historic stepwell with distinctive architecture."),("Kondajji Lake","Outdoor and nature destination."),("Harihareshwara Temple, Harihar","Temple on the Tungabhadra riverbank."),("Davanagere city food streets","Known for local benne dosa; choose hygienic, busy eateries.")],"stays":["Davanagere city hotels","Harihar town lodges"]},
 {"name":"Dharwad","landmark":"Chandramouleshwara Temple, Unkal","places":[("Chandramouleshwara Temple","Historic temple in the Hubballi-Dharwad area."),("Dharwad Sadhankeri","Park and lake area."),("Unkal Lake","Popular lakefront in Hubballi."),("Nrupatunga Betta","Hill viewpoint in Hubballi."),("Banashankari Temple, Amargol","Historic temple in the region.")],"stays":["Hubballi-Dharwad city hotels","Near railway station business hotels"]},
 {"name":"Gadag","landmark":"Trikuteshwara Temple","places":[("Trikuteshwara Temple","Historic temple complex with ornate pillars."),("Veeranarayana Temple, Gadag","Important medieval temple."),("Lakkundi","Heritage village with temples and stepwells."),("Dambal Doddabasappa Temple","Noted Chalukyan-era temple."),("Kappatagudda","Hills and biodiversity landscape; follow local guidance.")],"stays":["Gadag town hotels","Lakkundi-area guesthouses where available"]},
 {"name":"Hassan","landmark":"Hoysaleswara Temple, Halebidu","places":[("Hoysaleswara Temple, Halebidu","Highly detailed Hoysala stone temple."),("Chennakeshava Temple, Belur","Famous Hoysala temple complex."),("Shravanabelagola","Major Jain pilgrimage centre with monumental statue."),("Manjarabad Fort","Star-shaped hill fort near Sakleshpur."),("Shettihalli Rosary Church","Picturesque church ruins; water levels and access vary.")],"stays":["Hassan city hotels","Belur heritage-area stays","Sakleshpur coffee homestays"]},
 {"name":"Haveri","landmark":"Siddhesvara Temple, Haveri","places":[("Siddhesvara Temple","Historic temple with carved stonework."),("Bankapura Peacock Sanctuary","Wildlife area; follow forest rules."),("Byadgi","Town known for its chilli market."),("Utsav Rock Garden, Gotagodi","Outdoor sculpture and folk-art park.")],"stays":["Haveri town hotels","Ranebennur highway hotels"]},
 {"name":"Kalaburagi","landmark":"Sharana Basaveshwara Temple","places":[("Shar​​ana Basaveshwara Temple","Important pilgrimage temple."),("Gulbarga Fort","Historic fort and mosque architecture."),("Khwaja Bande Nawaz Dargah","Important Sufi shrine."),("Buddha Vihar","Peaceful Buddhist centre."),("Sannati","Archaeological and Buddhist heritage site in the wider district region.")],"stays":["Kalaburagi city hotels","Central-area business hotels"]},
 {"name":"Kodagu","landmark":"Talakaveri","places":[("Talakaveri","Source area of the Kaveri river and pilgrimage site."),("Bhagamandala","Temple town at the river confluence."),("Abbey Falls","Popular waterfall near Madikeri."),("Raja's Seat","Garden viewpoint in Madikeri."),("Dubare Elephant Camp","Managed visitor experience; check official rules."),("Mandalpatti","Scenic hill viewpoint; vehicle access may be restricted.")],"stays":["Madikeri town hotels","Registered coffee-estate homestays","Family-friendly resorts near main roads"]},
 {"name":"Kolar","landmark":"Kolaramma Temple","places":[("Kolaramma Temple","Historic temple with Chola-era features."),("Someshwara Temple, Kolar","Noted temple architecture."),("Antaragange","Hill, caves, and temple; trek with care."),("Kotilingeshwara Temple","Large Shiva temple complex in Kammasandra."),("Avani","Heritage village associated with Ramalingeshwara temples.")],"stays":["Kolar town hotels","Malur highway stays"]},
 {"name":"Koppal","landmark":"Mahadeva Temple, Itagi","places":[("Mahadeva Temple, Itagi","Important Kalyana Chalukya temple."),("Anegundi","Historic village across the river from Hampi."),("Anjanadri Hill","Pilgrimage hill associated with Hanuman traditions; many steps."),("Kanakagiri","Historic temple town."),("Pampa Sarovar","Pilgrimage site near Anegundi.")],"stays":["Koppal town hotels","Anegundi guesthouses","Hospet/Hampi stays for nearby circuits"]},
 {"name":"Mandya","landmark":"Melukote Cheluvanarayana Swamy Temple","places":[("Melukote Cheluvanarayana Swamy Temple","Important Vaishnava pilgrimage centre."),("Yoga Narasimha Temple, Melukote","Hilltop temple reached by steps."),("KRS Brindavan Gardens","Gardens near Krishna Raja Sagara dam; check show timings."),("Shivanasamudra Falls","Major waterfall in the Kaveri river system."),("Ranganathittu Bird Sanctuary","Bird sanctuary near Srirangapatna; use authorised boats.")],"stays":["Mandya town hotels","Srirangapatna/Mysuru-area stays","Mysuru-side family hotels for KRS visits"]},
 {"name":"Mysuru","landmark":"Mysuru Palace","places":[("Mysuru Palace","Iconic royal palace; check entry and illumination schedule."),("Chamundeshwari Temple","Hilltop temple on Chamundi Hills."),("St. Philomena's Church","Historic neo-Gothic church."),("Mysuru Zoo","Well-known zoological park."),("Jaganmohan Palace Art Gallery","Art and heritage collection."),("Karanji Lake","Urban nature park and bird habitat.")],"stays":["Mysuru city hotels","Heritage stays around the palace area","Family hotels near main roads"]},
 {"name":"Raichur","landmark":"Raichur Fort","places":[("Raichur Fort","Historic fort with inscriptions and gateways."),("Maski","Archaeological site associated with Ashokan inscription."),("Manvi Jagannathadasa temple sites","Regional devotional heritage."),("Narada Gadde","River-island pilgrimage destination; access depends on season.")],"stays":["Raichur city hotels","Sindhanur town lodges"]},
 {"name":"Ramanagara","landmark":"Ramadevara Betta","places":[("Ramadevara Betta","Hill and temple area known for rocky scenery."),("Janapada Loka","Folk culture museum near the highway."),("Kanva Reservoir","Scenic reservoir area; follow local restrictions."),("Channapatna toy workshops","Traditional lacquered wooden toy craft; buy from reputable makers."),("Mekedatu and Sangama","River landscape day trip; check seasonal access and safety.")],"stays":["Ramanagara town hotels","Kanakapura road resorts","Nature stays with verified access"]},
 {"name":"Shivamogga","landmark":"Jog Falls","places":[("Jog Falls","Major waterfall; flow and viewpoints vary by season."),("Keladi Rameshwara Temple","Historic temple in Keladi."),("Ikkeri Aghoreshwara Temple","Noted stone temple near Sagara."),("Kodachadri","Popular trekking and hill destination; plan permits/guide if required."),("Tyavarekoppa Lion and Tiger Safari","Managed wildlife visitor centre; check official timings."),("Sakrebailu Elephant Camp","Managed elephant interpretation centre; check official rules.")],"stays":["Shivamogga city hotels","Sagara/Jog Falls-area stays","Approved nature lodges"]},
 {"name":"Tumakuru","landmark":"Devarayanadurga","places":[("Devarayanadurga","Hill destination with temples and viewpoints."),("Yediyur Siddhalingeshwara Temple","Important pilgrimage centre."),("Madhugiri Fort","Large hill fort; trek only in suitable weather."),("Siddaganga Matha","Respected educational and spiritual institution."),("Namada Chilume","Natural spring and local heritage spot.")],"stays":["Tumakuru city hotels","Kunigal highway hotels"]},
 {"name":"Udupi","landmark":"Sri Krishna Matha","places":[("Sri Krishna Matha","Major Krishna temple and pilgrimage centre."),("Malpe Beach","Popular beach and boat departure point; follow sea warnings."),("St. Mary's Islands","Geological island formations; ferry access is seasonal."),("Kaup Lighthouse and Beach","Coastal landmark; check lighthouse opening."),("Kollur Mookambika Temple","Major temple in the wider coastal pilgrimage circuit."),("Hasta Shilpa Heritage Village","Heritage museum; check visiting schedule.")],"stays":["Udupi town hotels","Malpe beach-area stays","Kundapura family hotels"]},
 {"name":"Uttara Kannada","landmark":"Murudeshwar Temple and Shiva statue","places":[("Murudeshwar Temple","Coastal temple with a prominent Shiva statue."),("Gokarna Mahabaleshwar Temple","Important pilgrimage temple."),("Yana rock formations","Forest rock formations; wear suitable footwear."),("Dandeli wildlife and river activities","Use licensed operators and safety equipment."),("Unchalli Falls","Waterfall viewpoint; access may vary."),("Mirjan Fort","Historic fort near the coast.")],"stays":["Karwar/Kumta town hotels","Gokarna guesthouses","Licensed Dandeli nature resorts"]},
 {"name":"Vijayanagara","landmark":"Virupaksha Temple, Hampi","places":[("Hampi Group of Monuments","UNESCO World Heritage landscape."),("Virupaksha Temple","Living temple in Hampi's historic centre."),("Vittala Temple and Stone Chariot","Iconic Vijayanagara architecture."),("Hemakuta Hill","Temple-studded hill and sunset views; avoid unsafe edges."),("Queen's Bath and Royal Enclosure","Royal-era archaeological complex."),("Tungabhadra riverside","Historic landscape; obey river safety warnings.")],"stays":["Hospet hotels","Hampi guesthouses in permitted areas","Registered homestays around the heritage zone"]},
 {"name":"Vijayapura","landmark":"Gol Gumbaz","places":[("Gol Gumbaz","Famous mausoleum with a vast dome and whispering gallery."),("Ibrahim Rauza","Elegant historic tomb and mosque complex."),("Bara Kaman","Unfinished monumental mausoleum."),("Jamiya Masjid","Historic mosque in the old city."),("Almatti Dam and Rock Garden","Reservoir views and landscaped area.")],"stays":["Vijayapura city hotels","Central heritage-area hotels"]},
 {"name":"Yadgir","landmark":"Yadgir Fort","places":[("Yadgir Fort","Historic hill fort overlooking the town."),("Shorapur (Surpur)","Heritage town with palace and local history."),("Wagangera Fort","Historic fort remains; check local access."),("Sannati day trip","Buddhist and archaeological heritage in the wider region; verify travel distance.")],"stays":["Yadgir town hotels","Shorapur town lodges"]}
]

STYLES = {
 "Solo": "Flexible pace, public transport where practical, daytime visits, and well-reviewed central stays.",
 "Couple": "Scenic viewpoints, heritage walks, relaxed cafés, and comfortable stays.",
 "Family": "Shorter travel hops, accessible attractions, meal breaks, and family rooms.",
 "Friends": "Adventure options, shared stays, local food, and group-friendly activities."
}

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, district TEXT DEFAULT '', phone TEXT DEFAULT '',
            travel_style TEXT DEFAULT 'Solo'
        );
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            district TEXT NOT NULL, duration INTEGER NOT NULL, travel_style TEXT NOT NULL,
            start_date TEXT DEFAULT '', end_date TEXT DEFAULT '', notes TEXT DEFAULT '',
            created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            trip_id INTEGER, title TEXT NOT NULL, amount REAL NOT NULL,
            category TEXT NOT NULL, expense_date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            property_name TEXT NOT NULL, district TEXT NOT NULL, booking_type TEXT NOT NULL,
            check_in TEXT NOT NULL, check_out TEXT NOT NULL, guests INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Request submitted', created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            title TEXT NOT NULL, target_amount REAL DEFAULT 0, saved_amount REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
init_db()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to use that feature.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def current_user():
    if not session.get("user_id"):
        return None
    with db() as con:
        return con.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_globals():
    return {"districts": DISTRICTS, "styles": STYLES, "current_user": current_user()}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        district = request.form.get("district", "")
        style = request.form.get("travel_style", "Solo")
        if not all([full_name, username, email, password]):
            flash("Please fill in all required fields.", "error")
        elif len(password) < 6:
            flash("Use a password with at least 6 characters.", "error")
        else:
            try:
                with db() as con:
                    cur = con.execute("INSERT INTO users(full_name,username,email,password_hash,district,travel_style) VALUES(?,?,?,?,?,?)",
                        (full_name, username, email, generate_password_hash(password), district, style))
                    session["user_id"] = cur.lastrowid
                flash("Account created. Welcome to Trip Companion!", "success")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("That username or email is already registered. Try another.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE username=? OR email=?", (username, username.lower())).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Login details do not match. Please try again.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    with db() as con:
        trips = con.execute("SELECT * FROM trips WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
        expenses = con.execute("SELECT COALESCE(SUM(amount),0) total FROM expenses WHERE user_id=?", (uid,)).fetchone()["total"]
        bookings = con.execute("SELECT COUNT(*) n FROM bookings WHERE user_id=?", (uid,)).fetchone()["n"]
        goals = con.execute("SELECT COUNT(*) n FROM goals WHERE user_id=?", (uid,)).fetchone()["n"]
    return render_template("dashboard.html", trips=trips, expense_total=expenses, booking_count=bookings, goal_count=goals)

@app.route("/explorer")
def explorer():
    q = request.args.get("q", "").strip().lower()
    found = [d for d in DISTRICTS if not q or q in d["name"].lower() or q in d["landmark"].lower()
             or any(q in p[0].lower() or q in p[1].lower() for p in d["places"])]
    return render_template("explorer.html", found=found, q=q)

@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    selected = None
    itinerary = []
    duration = 1
    style = current_user()["travel_style"] or "Solo"
    if request.method == "POST":
        name = request.form.get("district", "")
        selected = next((d for d in DISTRICTS if d["name"] == name), None)
        try:
            duration = max(1, min(14, int(request.form.get("duration", "1"))))
        except ValueError:
            duration = 1
        style = request.form.get("travel_style", "Solo")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        notes = request.form.get("notes", "").strip()
        if selected:
            places = selected["places"]
            # Split the attraction list into manageable daily groups.
            per_day = max(1, (len(places) + duration - 1) // duration)
            for day in range(duration):
                chunk = places[day*per_day:(day+1)*per_day]
                if not chunk and places:
                    chunk = [places[day % len(places)]]
                itinerary.append({"day": day+1, "places": chunk})
            with db() as con:
                con.execute("INSERT INTO trips(user_id,district,duration,travel_style,start_date,end_date,notes,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (session["user_id"], name, duration, style, start_date, end_date, notes, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Itinerary created and saved to your trip history.", "success")
    return render_template("planner.html", selected=selected, itinerary=itinerary, duration=duration, chosen_style=style)

@app.route("/hotels")
def hotels():
    picks = []
    for d in DISTRICTS:
        for typ, desc in [
            ("Town hotel", "Choose a well-reviewed property close to transport, restaurants, and the places you plan to visit."),
            ("Family stay", "Ask about family rooms, clean bathrooms, drinking water, parking, and check-in rules."),
            ("Homestay / nature stay", "Prefer registered hosts, recent reviews, clear access details, and written cancellation terms.")
        ]:
            picks.append({"district": d["name"], "name": f"{d['name']} {typ}", "type": typ, "description": desc})
    q = request.args.get("district", "")
    if q:
        picks = [p for p in picks if p["district"] == q]
    return render_template("hotels.html", properties=picks, filter_district=q)

@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    if request.method == "POST":
        property_name = request.form.get("property_name", "").strip()
        district = request.form.get("district", "").strip()
        booking_type = request.form.get("booking_type", "Hotel")
        check_in = request.form.get("check_in", "")
        check_out = request.form.get("check_out", "")
        try:
            guests = max(1, min(30, int(request.form.get("guests", "1"))))
        except ValueError:
            guests = 1
        if not all([property_name, district, check_in, check_out]) or check_out < check_in:
            flash("Please enter the stay details and make sure check-out is not before check-in.", "error")
        else:
            with db() as con:
                con.execute("INSERT INTO bookings(user_id,property_name,district,booking_type,check_in,check_out,guests,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (session["user_id"], property_name, district, booking_type, check_in, check_out, guests, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Demo booking request saved. This is not a confirmed hotel reservation.", "success")
            return redirect(url_for("my_bookings"))
    return render_template("booking.html", today=date.today().isoformat())

@app.route("/my-bookings")
@login_required
def my_bookings():
    with db() as con:
        rows = con.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("my_bookings.html", bookings=rows)

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    uid = session["user_id"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Other")
        try:
            amount = float(request.form.get("amount", "0"))
        except ValueError:
            amount = 0
        expense_date = request.form.get("expense_date") or date.today().isoformat()
        if not title or amount <= 0:
            flash("Enter an expense name and an amount greater than zero.", "error")
        else:
            with db() as con:
                con.execute("INSERT INTO expenses(user_id,title,amount,category,expense_date) VALUES(?,?,?,?,?)",
                    (uid, title, amount, category, expense_date))
            flash("Expense added.", "success")
            return redirect(url_for("expenses"))
    with db() as con:
        rows = con.execute("SELECT * FROM expenses WHERE user_id=? ORDER BY expense_date DESC,id DESC", (uid,)).fetchall()
        total = con.execute("SELECT COALESCE(SUM(amount),0) total FROM expenses WHERE user_id=?", (uid,)).fetchone()["total"]
    return render_template("expenses.html", expenses=rows, total=total, today=date.today().isoformat())

@app.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    with db() as con:
        con.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, session["user_id"]))
    flash("Expense removed.", "success")
    return redirect(url_for("expenses"))

@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    uid = session["user_id"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        try:
            target = max(0, float(request.form.get("target_amount", "0")))
        except ValueError:
            target = 0
        if title:
            with db() as con:
                con.execute("INSERT INTO goals(user_id,title,target_amount) VALUES(?,?,?)", (uid, title, target))
            flash("Travel goal added.", "success")
            return redirect(url_for("goals"))
        flash("Please enter a goal name.", "error")
    with db() as con:
        rows = con.execute("SELECT * FROM goals WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    return render_template("goals.html", goals=rows)

@app.route("/goals/delete/<int:goal_id>", methods=["POST"])
@login_required
def delete_goal(goal_id):
    with db() as con:
        con.execute("DELETE FROM goals WHERE id=? AND user_id=?", (goal_id, session["user_id"]))
    flash("Goal removed.", "success")
    return redirect(url_for("goals"))

@app.route("/history")
@login_required
def history():
    with db() as con:
        trips = con.execute("SELECT * FROM trips WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("history.html", trips=trips)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    uid = session["user_id"]
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        district = request.form.get("district", "")
        style = request.form.get("travel_style", "Solo")
        try:
            with db() as con:
                con.execute("UPDATE users SET full_name=?,email=?,phone=?,district=?,travel_style=? WHERE id=?",
                            (full_name, email, phone, district, style, uid))
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
        except sqlite3.IntegrityError:
            flash("That email is already used by another account.", "error")
    user = current_user()
    return render_template("profile.html", user=user)

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
