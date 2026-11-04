# KTV BOOKING WITH RECEIPT SYSTEM
# KTV Room Scheduling and Session Monitoring System (console-based, with login)

from datetime import datetime, timedelta

schedules = []
rooms = ["Room 1", "Room 2", "Room 3", "Room 4", "Room 5", "VIP Room"]

room_price = {
    "Room 1": 100,
    "Room 2": 100,
    "Room 3": 100,
    "Room 4": 100,
    "Room 5": 100,
    "VIP Room": 250,
}

# Default users
users = {
    "admin": {"password": "admin123", "role": "admin"},
}

total_revenue = 0          # only grows when admin records a customer's payment
MAX_HOURS = 12
STATUS_OPTIONS = ["Pending", "Confirmed", "In Session", "Completed", "Cancelled"]


# ========== HELPERS ==========
def start_of(s):
    """Start datetime of a booking."""
    return datetime.strptime(f"{s['date']} {s['time']}", "%m-%d-%y %I:%M %p")


def end_of(s):
    return start_of(s) + timedelta(hours=s["hours"])


def is_active(s):
    """Bookings that still hold a room / count against the customer."""
    return s["status"] in ("Pending", "Confirmed", "In Session")


def has_overlap(room, start, hours, ignore=None):
    """OVERBOOK check: True if the room is taken during [start, start+hours)."""
    end = start + timedelta(hours=hours)
    for s in schedules:
        if s is ignore or s["room"] != room or not is_active(s):
            continue
        if start < end_of(s) and start_of(s) < end:
            return True
    return False


def print_receipt(s, paid, change):
    print("\n----- KTV OFFICIAL RECEIPT -----")
    print(f"Customer: {s['customer']}")
    print(f"Room: {s['room']}")
    print(f"Date: {s['date']}")
    print(f"Time: {s['time']}")
    print(f"Hours: {s['hours']}")
    print(f"Price per hour: P{room_price.get(s['room'], 0)}")
    print(f"Total Amount: P{s['total']}")
    print(f"Amount Paid: P{paid}")
    print(f"Change: P{change}")
    print("--------------------------------")
    print("Payment received. Thank you!")


def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("Invalid input. Please enter 'yes' or 'no'.")


def ask_int(prompt, low=None, high=None):
    """Returns int or None if invalid."""
    try:
        value = int(input(prompt))
    except ValueError:
        return None
    if low is not None and value < low:
        return None
    if high is not None and value > high:
        return None
    return value


def ask_date():
    """Ask for a valid booking date. Returns (date_str, date_obj) or None to cancel."""
    while True:
        date = input("Enter Date (MM-DD-YY, e.g., 12-25-26) or 0 to cancel: ").strip()
        if date == "0":
            return None
        try:
            date_obj = datetime.strptime(date, "%m-%d-%y")
        except ValueError:
            print("Invalid date. Please use MM-DD-YY and a real calendar date.")
            continue
        if date_obj.date() < datetime.now().date():
            print("You cannot book a date in the past.")
            continue
        if date_obj.date() > (datetime.now() + timedelta(days=365)).date():
            print("You can only book up to 1 year ahead.")
            continue
        return date, date_obj


def ask_time(date_obj):
    """Ask for a valid start time. Returns (start_datetime, time_str)."""
    while True:
        time_in = input("Enter time (e.g., 6:00 PM): ").strip().upper()
        try:
            time_obj = datetime.strptime(time_in, "%I:%M %p")
        except ValueError:
            print("Invalid time. Please use HH:MM AM/PM (e.g., 6:00 PM).")
            continue
        start = datetime.combine(date_obj.date(), time_obj.time())
        if start <= datetime.now():
            print("That time has already passed. Please choose a later time.")
            continue
        return start, time_obj.strftime("%I:%M %p").lstrip("0")


def ask_hours():
    while True:
        hours = ask_int(f"Enter Hours (1-{MAX_HOURS}): ", 1, MAX_HOURS)
        if hours is None:
            print(f"Invalid number of hours. Enter a whole number from 1 to {MAX_HOURS}.")
            continue
        return hours


def fmt_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0")


def fmt_remaining(delta):
    mins = int(delta.total_seconds() // 60)
    return f"{mins // 60}h {mins % 60}m"


def print_booking_receipt(s):
    """Receipt shown to the customer when the booking is made."""
    print("\n----- KTV RECEIPT -----")
    print(f"Customer: {s['customer']}")
    print(f"Room: {s['room']}")
    print(f"Date: {s['date']}")
    print(f"Time: {s['time']}")
    print(f"Hours: {s['hours']}")
    print(f"Price per hour: P{room_price.get(s['room'], 0)}")
    print(f"Total Amount: P{s['total']}")
    print(f"Status: {s['status']}")
    print("-----------------------")


# ========== REGISTER / LOGIN ==========
def register():
    print("\n--- CUSTOMER REGISTER ---")

    while True:
        raw = input("Enter Username (lastname,birth year) or 0 to go back: ").strip()

        if raw == "0":
            return

        parts = raw.split(",")
        if len(parts) != 2:
            print("Invalid format!")
            print("Example: Satsat,2008")
            continue

        lastname = parts[0].strip()
        birth_year = parts[1].strip()

        if lastname == "" or not birth_year.isdigit() or len(birth_year) != 4:
            print("Invalid username format!")
            print("Example: Satsat,2008")
            continue

        if not (1900 <= int(birth_year) <= datetime.now().year):
            print("Invalid birth year!")
            continue

        username = f"{lastname},{birth_year}"

        if username in users:
            print("Username already exists!")
            continue

        break

    while True:
        password = input("Create password (8 characters minimum): ")

        if len(password) < 8:
            print("Password must be at least 8 characters!")
            print("Try again.")
            continue

        confirm = input("Confirm password: ")
        if confirm != password:
            print("Passwords do not match!")
            continue

        break

    users[username] = {"password": password, "role": "customer"}

    print("Registration successful!")
    print("You can now login.")


def login():
    print("\n--- LOGIN --- (type 0 as username to go back)")

    attempts = 0
    while attempts < 3:
        username = input("Username: ").strip()

        if username == "0":
            return

        password = input("Password: ")

        # one generic message so we don't reveal which part was wrong
        if username not in users or users[username]["password"] != password:
            attempts += 1
            print(f"Invalid username or password! ({3 - attempts} attempt(s) left)")
            continue

        print(f"\nWelcome, {username}!")

        if users[username]["role"] == "admin":
            admin_menu()
        else:
            customer_menu(username)
        return

    print("Too many failed attempts. Returning to main menu.")


# ========== CUSTOMER FUNCTIONS ==========
def book_room(username):
    # one active booking per account
    for s in schedules:
        if s["customer"] == username and is_active(s):
            print("\nYou already have an active room booking.")
            print("One account can only book one room at a time.")
            return

    if not rooms:
        print("\nNo rooms available right now.")
        return

    print("\n========== KTV ROOM LIST ==========")
    for i, r in enumerate(rooms, 1):
        print(f"{i}. {r} - P{room_price[r]} per hour")
    print("0. Cancel")
    print("===================================")

    # room (pick by number)
    while True:
        choice = input(f"Choose room (1-{len(rooms)}, 0 to cancel): ").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(rooms):
            room = rooms[int(choice) - 1]
            print(f"You picked: {room}")
            break
        print(f"Invalid choice. Please enter a number from 1 to {len(rooms)}.")

    # date / time / hours (INPUT VALIDATION)
    result = ask_date()
    if result is None:
        return
    date, date_obj = result
    start, time_str = ask_time(date_obj)
    hours = ask_hours()

    # OVERBOOK check (covers overlapping hours, not just identical start time)
    if has_overlap(room, start, hours):
        print("\nSorry, that room is already booked during that time.")
        print("Please choose another time or room.")
        return

    price_per_hour = room_price[room]
    total = hours * price_per_hour
    end = start + timedelta(hours=hours)

    # CONFIRMATION before saving
    print("\n----- BOOKING SUMMARY -----")
    print(f"Customer: {username}")
    print(f"Room: {room}")
    print(f"Date: {date}")
    print(f"Time: {time_str} to {end.strftime('%I:%M %p').lstrip('0')}")
    print(f"Hours: {hours}")
    print(f"Price per hour: P{price_per_hour}")
    print(f"Total Amount: P{total}")
    print("---------------------------")

    if not ask_yes_no("Confirm this booking? (yes/no): "):
        print("Booking not saved.")
        return

    schedules.append({
        "customer": username,
        "room": room,
        "date": date,
        "time": time_str,
        "hours": hours,
        "total": total,
        "status": "Pending",   # goes to the admin's pending list
        "paid": False,
    })

    print("\nBooking submitted!")
    print_booking_receipt(schedules[-1])
    print("Status: Pending. Please wait for the admin to confirm your booking.")
    print("Payment is made at the counter and handled by the admin.")


def edit_booking(username):
    print("\n--- EDIT MY BOOKING ---")
    target = next((s for s in schedules
                   if s["customer"] == username and is_active(s)), None)

    if target is None:
        print("You have no active booking to edit.")
        return
    if target["status"] != "Pending":
        print(f"Your booking is already {target['status']}.")
        print("Only Pending bookings can be edited. Please ask the admin.")
        return

    print(f"Current: {target['room']} | {target['date']} | {target['time']} | "
          f"{target['hours']} hour(s) | P{target['total']}")
    print("Enter the new details.")

    result = ask_date()
    if result is None:
        print("Edit cancelled.")
        return
    date, date_obj = result
    start, time_str = ask_time(date_obj)
    hours = ask_hours()

    if has_overlap(target["room"], start, hours, ignore=target):
        print("\nSorry, that room is already booked during that time.")
        print("Your booking is unchanged.")
        return

    total = hours * room_price[target["room"]]
    print(f"\nNew: {target['room']} | {date} | {time_str} | {hours} hour(s) | P{total}")

    if not ask_yes_no("Save these changes? (yes/no): "):
        print("Changes not saved.")
        return

    target["date"] = date
    target["time"] = time_str
    target["hours"] = hours
    target["total"] = total
    print("\nBooking updated!")
    print_booking_receipt(target)


def customer_menu(username):
    while True:
        print(f"\n--- CUSTOMER MENU ({username}) ---")
        print("1. Book a Room")
        print("2. View My Bookings")
        print("3. Cancel My Booking")
        print("4. Edit My Booking")
        print("5. Logout")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            book_room(username)
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n--- MY BOOKINGS ---")
            found = False
            for s in schedules:
                if s["customer"] == username and s["status"] != "Cancelled":
                    print("Room:", s["room"])
                    print("Date:", s["date"])
                    print("Time:", s["time"])
                    print("Hours:", s["hours"])
                    print("Total: P", s["total"])
                    print("Status:", s["status"])
                    print("Payment:", "Paid" if s.get("paid") else "Unpaid")
                    if s["status"] == "In Session":
                        left = s["session_start"] + timedelta(hours=s["hours"]) - datetime.now()
                        if left.total_seconds() > 0:
                            print("Time left:", fmt_remaining(left))
                        else:
                            print("Time left: session time is over")
                    print("--------------------")
                    found = True
            if not found:
                print("You have no bookings.")
            input("Press Enter to continue...")

        elif choice == "3":
            print("\n--- CANCEL MY BOOKING ---")
            target = next((s for s in schedules
                           if s["customer"] == username and is_active(s)), None)

            if target is None:
                print("You have no active booking to cancel.")
            elif target["status"] == "In Session":
                print("Your session has already started. It cannot be cancelled.")
            elif target.get("paid"):
                print("This booking is already paid. Please ask the admin to cancel it.")
            else:
                print("\nRoom:", target["room"])
                print("Date:", target["date"])
                print("Time:", target["time"])
                print("Status:", target["status"])

                if ask_yes_no("\nAre you sure you want to cancel? (yes/no): "):
                    target["status"] = "Cancelled"
                    print("Your booking has been cancelled.")
                else:
                    print("Cancellation stopped. Your booking is unchanged.")
            input("\nPress Enter to continue...")

        elif choice == "4":
            edit_booking(username)
            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\nYou have logged out successfully.")
            break

        else:
            print("Invalid choice. Please choose 1-5.")
            input("Press Enter to continue...")


# ========== ADMIN FUNCTIONS ==========
def show_schedule_line(i, s):
    print(f"{i}. Customer: {s['customer']} | Room: {s['room']} | Date: {s['date']} | "
          f"Time: {s['time']} | Hours: {s['hours']} | Total: P{s['total']} | "
          f"Status: {s['status']} | {'Paid' if s.get('paid') else 'Unpaid'}")


def pending_list():
    """PENDING LIST -> CONFIRM BY ADMIN"""
    print("\n--- PENDING LIST ---")
    pending = [s for s in schedules if s["status"] == "Pending"]

    if not pending:
        print("No pending bookings.")
        return

    for i, s in enumerate(pending, 1):
        show_schedule_line(i, s)

    num = ask_int("\nEnter number to review (0 to go back): ", 0, len(pending))
    if num is None:
        print("Invalid input.")
        return
    if num == 0:
        return

    s = pending[num - 1]

    # re-check overbook in case something changed since it was requested
    if has_overlap(s["room"], start_of(s), s["hours"], ignore=s):
        print("Warning: this booking now overlaps with another active booking.")

    print("\n1. Confirm booking")
    print("2. Reject (cancel) booking")
    print("3. Back")
    action = input("Choose (1-3): ").strip()

    if action == "1":
        if has_overlap(s["room"], start_of(s), s["hours"], ignore=s):
            print("Cannot confirm: the room is double-booked at that time.")
            return
        s["status"] = "Confirmed"
        print(f"Booking of {s['customer']} confirmed.")
    elif action == "2":
        s["status"] = "Cancelled"
        print(f"Booking of {s['customer']} rejected.")
    elif action != "3":
        print("Invalid choice.")


def customer_payment():
    """BAYAD NI CUSTOMER -> CONFIRMED BOOK TOTAL -> ENTER AMOUNT -> RECEIPT -> ADD REVENUE"""
    global total_revenue

    print("\n--- CUSTOMER PAYMENT ---")
    unpaid = [s for s in schedules if s["status"] == "Confirmed" and not s.get("paid")]

    if not unpaid:
        print("No confirmed bookings waiting for payment.")
        return

    for i, s in enumerate(unpaid, 1):
        print(f"{i}. Customer: {s['customer']} | Room: {s['room']} | Date: {s['date']} | "
              f"Time: {s['time']} | Total: P{s['total']}")

    num = ask_int("\nEnter number of customer paying (0 to go back): ", 0, len(unpaid))
    if num is None:
        print("Invalid input.")
        return
    if num == 0:
        return

    s = unpaid[num - 1]
    print(f"\nTotal to pay for {s['customer']}: P{s['total']}")

    while True:
        raw = input("Enter amount received (0 to cancel): P").strip()
        try:
            amount = float(raw)
        except ValueError:
            print("Invalid amount. Please enter a number.")
            continue

        if amount == 0:
            print("Payment cancelled.")
            return
        if amount < s["total"]:
            print(f"Not enough. The total is P{s['total']}.")
            continue
        break

    change = amount - s["total"]
    s["paid"] = True
    total_revenue += s["total"]          # ADD REVENUE

    print_receipt(s, f"{amount:g}", f"{change:g}")


def room_board():
    """Live status of every room: In Session / Reserved / Available."""
    now = datetime.now()
    print("\n--- ROOM STATUS BOARD ---")
    print(f"As of {now.strftime('%m-%d-%y')} {fmt_time(now)}")
    for r in rooms:
        live = next((s for s in schedules
                     if s["room"] == r and s["status"] == "In Session"), None)
        if live:
            left = live["session_start"] + timedelta(hours=live["hours"]) - now
            if left.total_seconds() > 0:
                info = f"time left {fmt_remaining(left)}"
            else:
                info = f"OVERTIME by {fmt_remaining(-left)}"
            print(f"{r}: IN SESSION - {live['customer']} ({info})")
            continue

        upcoming = sorted((s for s in schedules
                           if s["room"] == r and s["status"] in ("Pending", "Confirmed")
                           and end_of(s) > now), key=start_of)
        if upcoming:
            n = upcoming[0]
            print(f"{r}: RESERVED - {n['customer']} on {n['date']} at {n['time']} "
                  f"({n['status']})")
        else:
            print(f"{r}: AVAILABLE")


def start_session():
    ready = [s for s in schedules if s["status"] == "Confirmed" and s.get("paid")]
    print("\n--- START SESSION ---")
    if not ready:
        print("No confirmed and paid bookings ready to start.")
        print("(The booking must be confirmed and paid first.)")
        return

    for i, s in enumerate(ready, 1):
        print(f"{i}. {s['customer']} | {s['room']} | {s['date']} {s['time']} | {s['hours']}h")

    num = ask_int("Enter number to start (0 to go back): ", 0, len(ready))
    if num is None:
        print("Invalid input.")
        return
    if num == 0:
        return

    s = ready[num - 1]
    if any(x["room"] == s["room"] and x["status"] == "In Session" for x in schedules):
        print(f"{s['room']} still has a session running. End it first.")
        return
    if start_of(s).date() != datetime.now().date():
        print(f"Warning: this booking is for {s['date']}, not today.")
        if not ask_yes_no("Start the session anyway? (yes/no): "):
            return

    s["status"] = "In Session"
    s["session_start"] = datetime.now()
    end = s["session_start"] + timedelta(hours=s["hours"])
    print(f"\nSession started for {s['customer']} in {s['room']}.")
    print(f"Started: {fmt_time(s['session_start'])} | Ends: {fmt_time(end)} ({s['hours']}h)")


def end_session():
    live = [s for s in schedules if s["status"] == "In Session"]
    print("\n--- END SESSION ---")
    if not live:
        print("No sessions are running.")
        return

    now = datetime.now()
    for i, s in enumerate(live, 1):
        left = s["session_start"] + timedelta(hours=s["hours"]) - now
        info = (f"time left {fmt_remaining(left)}" if left.total_seconds() > 0
                else f"OVERTIME by {fmt_remaining(-left)}")
        print(f"{i}. {s['customer']} | {s['room']} | started {fmt_time(s['session_start'])} | {info}")

    num = ask_int("Enter number to end (0 to go back): ", 0, len(live))
    if num is None:
        print("Invalid input.")
        return
    if num == 0:
        return

    s = live[num - 1]
    if ask_yes_no(f"End the session of {s['customer']}? (yes/no): "):
        s["status"] = "Completed"
        s["session_end"] = datetime.now()
        used = s["session_end"] - s["session_start"]
        print(f"Session ended. Time used: {fmt_remaining(used)} (booked {s['hours']}h).")
        print(f"{s['room']} is now available.")


def session_monitor():
    while True:
        print("\n--- SESSION MONITORING ---")
        print("1. Room Status Board")
        print("2. Start Session")
        print("3. End Session")
        print("4. Back")
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            room_board()
        elif choice == "2":
            start_session()
        elif choice == "3":
            end_session()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please choose 1-4.")


def edit_room_price():
    print("\n--- EDIT ROOM PRICE ---")
    for i, r in enumerate(rooms, 1):
        print(f"{i}. {r} - P{room_price[r]} per hour")
    num = ask_int("Enter room number (0 to go back): ", 0, len(rooms))
    if num is None:
        print("Invalid input.")
        return
    if num == 0:
        return
    r = rooms[num - 1]
    price = ask_int(f"Enter new price per hour for {r}: P", 1)
    if price is None:
        print("Invalid price. Price unchanged.")
        return
    room_price[r] = price
    print(f"{r} is now P{price} per hour. (Existing bookings keep their old total.)")


def admin_menu():
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. View All Schedules")
        print("2. View All Users")
        print("3. Pending List (Confirm Bookings)")
        print("4. Customer Payment")
        print("5. Delete Any Booking")
        print("6. Add Room")
        print("7. Remove Room")
        print("8. Add New Admin")
        print("9. Delete User")
        print("10. Update Booking Status")
        print("11. View Total Revenue")
        print("12. Edit Room Price")
        print("13. Session Monitoring")
        print("14. Logout")

        choice = input("Choose (1-14): ").strip()

        if choice == '1':
            print("\n--- ALL CUSTOMER SCHEDULES ---")
            if not schedules:
                print("No schedules yet.")
            else:
                for i, s in enumerate(schedules, 1):
                    show_schedule_line(i, s)

        elif choice == '2':
            print("\n--- ALL USERS ---")
            for u, data in users.items():
                print(f"Username: {u} | Role: {data['role']}")

        elif choice == '3':
            pending_list()

        elif choice == '4':
            customer_payment()

        elif choice == '5':
            if not schedules:
                print("No schedules to delete.")
                continue
            for i, s in enumerate(schedules, 1):
                print(f"{i}. Customer: {s['customer']} | Room: {s['room']} | Date: {s['date']}")
            num = ask_int("Enter number to delete: ", 1, len(schedules))
            if num is None:
                print("Invalid input.")
            elif ask_yes_no("Are you sure? (yes/no): "):
                removed = schedules.pop(num - 1)
                print(f"Deleted booking of {removed['customer']}.")
            else:
                print("Deletion cancelled.")

        elif choice == '6':
            print("\n--- ADD ROOM ---")
            new_room = input("Enter new room name: ").strip()
            if not new_room:
                print("Room name cannot be empty.")
            elif new_room.lower() in [r.lower() for r in rooms]:
                print("Room already exists!")
            else:
                price = ask_int("Enter price per hour: P", 1)
                if price is None:
                    print("Invalid price. Room not added.")
                else:
                    rooms.append(new_room)
                    room_price[new_room] = price
                    print(f"'{new_room}' added successfully at P{price}/hour.")

        elif choice == '7':
            print("\n--- REMOVE ROOM ---")
            print("Current Rooms:", ", ".join(rooms))
            room_to_remove = input("Enter room name to remove: ").strip()
            if room_to_remove not in rooms:
                print("Room not found.")
            elif any(s["room"] == room_to_remove and is_active(s) for s in schedules):
                print("Cannot remove: this room has active bookings.")
            else:
                rooms.remove(room_to_remove)
                room_price.pop(room_to_remove, None)
                print(f"'{room_to_remove}' removed successfully.")

        elif choice == '8':
            print("\n--- ADD NEW ADMIN ---")

            while True:
                new_admin = input("Enter new admin username: ").strip()

                if len(new_admin) < 3:
                    print("Invalid username! Use at least 3 characters.\n")
                elif not new_admin.replace("_", "").isalnum():
                    print("Invalid username! Use only letters, numbers, or underscores.\n")
                elif new_admin in users:
                    print("Username already exists! Please try another.\n")
                else:
                    break

            while True:
                new_password = input("Enter admin password (at least 8 characters): ")
                if len(new_password) < 8:
                    print("Invalid password! It must be at least 8 characters.\n")
                else:
                    break

            users[new_admin] = {"password": new_password, "role": "admin"}
            print("\nNew admin account successfully created!")
            input("Press Enter to continue...")

        elif choice == '9':
            print("\n--- DELETE USER ---")
            target = input("Enter username to delete: ").strip()
            if target == "admin":
                print("Cannot delete the default admin account.")
            elif target not in users:
                print("User not found.")
            elif ask_yes_no(f"Delete '{target}'? (yes/no): "):
                del users[target]
                print(f"User '{target}' deleted successfully.")

        elif choice == '10':
            print("\n--- UPDATE BOOKING STATUS ---")
            if not schedules:
                print("No schedules yet.")
                continue
            for i, s in enumerate(schedules, 1):
                show_schedule_line(i, s)
            num = ask_int("Enter number to update: ", 1, len(schedules))
            if num is None:
                print("Invalid input.")
                continue
            target = schedules[num - 1]
            print("Status options:", ", ".join(STATUS_OPTIONS))
            new_status = input("Enter new status: ").strip().title()
            if new_status not in STATUS_OPTIONS:
                print("Invalid status.")
            elif new_status == "In Session":
                print("Use 'Session Monitoring' > 'Start Session' to start a session.")
            elif new_status == "Completed" and not target.get("paid"):
                print("Cannot complete an unpaid booking. Use 'Customer Payment' first.")
            elif new_status in ("Pending", "Confirmed") and has_overlap(
                    target["room"], start_of(target), target["hours"], ignore=target):
                print("Cannot set: the room is booked by someone else at that time.")
            else:
                target["status"] = new_status
                print("Status updated.")

        elif choice == '11':
            print(f"\n--- TOTAL REVENUE ---\nP{total_revenue}")

        elif choice == '12':
            edit_room_price()

        elif choice == '13':
            session_monitor()

        elif choice == '14':
            print("\nYou have logged out successfully.")
            break

        else:
            print("Invalid choice. Please choose 1-14.")


# ========== MAIN SYSTEM ==========
while True:
    print("\n==================================================")
    print(" KTV ROOM SCHEDULING AND SESSION MONITORING SYSTEM")
    print("==================================================")
    print("1. Login")
    print("2. Register")
    print("3. Exit")

    main_choice = input("Choose (1-3): ").strip()

    if main_choice == '1':
        login()
    elif main_choice == '2':
        register()
    elif main_choice == '3':
        print("Thank you for using the KTV Room Scheduling and Session Monitoring System. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        input("Press Enter to return to the main menu...")
