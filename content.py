import requests

payload = {'username:hikari', 'password:hikari'}
s = requests.session()

print s.get('http://localhost:8080/users/6').content

r = s.post('http://localhost:8080/users/login', data=payload)
r = s.post('http://localhost:8080/users/login', cookie={'ticket': "xxx"}).content
# print r.content

print s.get('http://localhost:8080/users/6').content
