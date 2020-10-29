from bs4 import BeautifulSoup


def send_registration_form(tested_app, url, form):
    reply = tested_app.t_post(url, data=form)
    soup = BeautifulSoup(reply.get_data(as_text=True), 'html.parser')
    helpblock = soup.find_all('p', attrs={'class': 'help-block'})

    if helpblock == []:
        helpblock = ""
    else:
        helpblock = helpblock[0].text.strip()

    return {"status_code":reply.status_code, "help-block":helpblock}

def do_login(client, email, password):
    return client.t_post('/login',data={"email":email, "password": password})

def do_logout(client):
    return client.t_get('/logout')