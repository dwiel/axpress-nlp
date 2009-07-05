require 'python'

pg = python.globals()
python.execute("env = {'vars' : {}}")
pg.env.place = 'indiana'

pg.wrapper = "def __foo() :\n %s\n\n__ret = __foo()"
pg.code = "import metaweb\nquery = [{ 'name':place, '/location/location/area':None }]\nplaces = metaweb.read(query)\nif places :\n return str(places[0]['/location/location/area']) + ' km^2'"
python.execute("print wrapper % code.replace('\\n', '\\n ')")
python.execute("exec wrapper % code.replace('\\n', '\\n ') in env")
if pg.env.__ret then
	print(pg.env.__ret)
else
	print("bah!")
end