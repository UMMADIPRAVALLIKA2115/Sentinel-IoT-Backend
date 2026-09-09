@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        # If they type 'guest', they skip the OTP!
        if user == "guest":
            session['logged_in'] = True
            return redirect(url_for('index'))
            
        if user == "admin" and pw == "hyderabad2026":
            # ... keep your existing OTP logic here for your own demo ...