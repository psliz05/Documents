# Grade Checker

A simple script that logs into **my.harvard**, checks all of your class grades, and emails you whenever something changes!

---

## Quick Setup

1. **Clone / Download** this from GitHub

   `git clone https://github.com/psliz05/grade-checker.git`
   
   `cd grade-checker`

3. Install requirements

   `pip install selenium`

4. Google App Password

You can’t just use your normal password to send emails to yourself. Create an app password:

note: this only works for your personal email. use that, not your harvard email, for 'Gmail creds.'
- go to this link: https://myaccount.google.com/apppasswords (under your personal gmail account).
- enter some 'app name,' and press create.
- copy that 16-character password and use it for GMAIL_PASSWORD (next step).

5. enter the environment variables in the terminal

    **Harvard Key creds**
   
    `export HARVARD_USERNAME="myharvarduser"`
   
    `export HARVARD_PASSWORD="myharvardpass"`

    **Gmail creds (see previous section on app password!)**
   
    `export GMAIL_USERNAME="mygmail@gmail.com"`
   
    `export GMAIL_PASSWORD="abcdefghijklmnop"`

7. run the script

    `python3 grades.py`

# YOU WILL HAVE TO ACCEPT THE DUO PUSH THE FIRST TIME. THEN IT CAN JUST RUN FOREVER.
