import re

def send_registration_form(tested_app, url, form):
    reply = tested_app.t_post(url, data=form)
    return {"status_code":reply.status_code, "html": reply.get_data(as_text=True)}

def do_login(client, email, password):
    return client.t_post('/login',data={"email":email, "password": password})

def do_logout(client):
    return client.t_get('/logout')

def edit_restaurant(client, id, data):
    return client.t_post("/restaurants/"+str(id)+"/edit", data=data)

def get_restaurant_id(client, name=""):
    reply = client.t_get('/restaurants')
    text = reply.get_data(as_text=True)
    text = text[text.find(name):]
    matches = re.findall(r"\/restaurants\/([0-9]+)[^0-9]+",text)
    try:
        id = matches[0]
        id = int(id)
    except:
        return None
    return id

def get_my_restaurant_id(client, name=""):
    reply = client.t_get('/')
    text = reply.get_data(as_text=True)
    text = text[text.find(name):]
    matches = re.findall(r"\/restaurants\/([0-9]+)[^0-9]+",text)
    try:
        id = matches[0]
        id = int(id)
    except:
        return None
    return id

def get_tables_ids(client, rest_id):
    reply = client.t_get('/restaurants/'+str(rest_id))
    matches = re.findall(r"\/tables\/([0-9]+)[^0-9]+",reply.get_data(as_text=True))
    return list(dict.fromkeys([int(match) for match in matches])) # unique ids

def get_positives_id(client):
    reply = client.t_get("/positives")
    matches = re.findall(r"\/positives\/([0-9]+)\/unmark",reply.get_data(as_text=True))
    return [int(match) for match in matches]

def get_restaurant_likes(client, rest_id):
    reply = client.t_get('/restaurants/'+str(rest_id))
    matches = re.findall(r"([0-9]+) Likes",reply.get_data(as_text=True))
    if len(matches) != 1:
        return None
    return matches[0]