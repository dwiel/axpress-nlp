require "etree"
require "luasql.mysql"
require "python"
local sql = luasql.mysql()
local con
-- local con = sql:connect("english", "root", "badf00d")

require "matching"
require "sparql"

-- some python code
python.execute([[
class Iter():
	def __init__(self, list) :
		self.i = list.__iter__()
	def __call__(self) :
		try :
			return self.i.next()
		except StopIteration :
			return '__stopiteration__'
]])


debugp = function () end

-- an iterator form the luasql examples page
function rows (connection, sql_statement)
  local cursor = assert (connection:execute (sql_statement))
  return function ()
    return cursor:fetch()
  end
end

local function get_language_id(language)
  local sqlquery = "SELECT language_id FROM languages WHERE name = '"..language.."'"
  local cur = con:execute(sqlquery)
  local row = cur:fetch({}, "a")
  if row == nil then return 0 end
  return row['language_id']
end

function get_varname_from_matchtype(matchtype)
	local var = matchtype:match(":%s*(.*)")
	if var == nil then
		return matchtype
	else
		return var
	end
end

function get_language_and_matchtype_from_matchtype(matchtype, language)
	local new_matchtype = matchtype:match("(.*)%s*:")
  if new_matchtype then
    matchtype = new_matchtype
	end
  local new_language, new_matchtype = matchtype:match("([^/]*)/(.*)")
  if new_language then
    return new_language, new_matchtype
  else
    return language, matchtype
  end
end

local function ffalse() return false end
local function get_function(id, vars)
	-- we need to retrieve and compile the function
	local sqlquery = "SELECT function, type FROM functions WHERE function_id='"..id.."'"
	local cur = con:execute(sqlquery)
	local row = cur:fetch ({}, "a")
	if row == nil then return ffalse end
	local code = row['function']
	local code_language = row['type']
  
	if code_language == 'function' then
		-- compile
		local env = {os = {date = os.date, time = os.time}, 
									string = string, 
									tonumber = tonumber,
									print = print,
									table = table,
									math = math,
									vars = vars,
									pairs = pairs,
									ipairs = ipairs,
									forwardto = forwardto}
		for k, v in pairs(exec_env) do
			env[k] = v
		end
		
		local f, err = loadstring(code)
		if type(f) ~= "function" then
			error(err)
		end
    
		setfenv(f, env)
		return f(), env
	elseif code_language == 'python' then
		pg = python.globals()
		python.execute("env = {}")
		
		for k, v in pairs(vars) do
			pg.env[k] = v
		end
		
		-- python.execute("env['__builtins__'] = None")
		pg.wrapper = "def __foo() :\n %s\n\n__ret = __foo()"
		pg.code = code
		-- do nothing in python, just to initialize the env.  It gets filled with
		-- a bunch of things we don't want in the vars
		python.execute("exec '' in env")
		local env1 = {}
		iter = python.eval("Iter(env)")
		k = iter()
		while k ~= '__stopiteration__' do
			env1[k] = pg.env[k]
			k = iter()
		end
		
		-- now run the code
		python.execute("exec code.replace('\\r\\n', '\\n') in env")
		local env = {}
		iter = python.eval("Iter(env)")
		k = iter()
		while k ~= '__stopiteration__' do
			-- only copy values that weren't in the original env
			if not env1[k] then
				env[k] = pg.env[k]
			end
			k = iter()
		end
		
		if pg.env.__ret then
			return pg.env.__ret, env
		else
			return "bah!", env
		end
	end
end

match_query_cache = {}

function clear_match_query_cache()
	match_query_cache = {}
end

-- the type is optional.  If it is specified, only queries resulting in that
-- type will be returned
function match_query(language_id, query, result_type)
	local results = {}
	local sqlquery = ""

	totalmatches = totalmatches + 1
		
-- 	if result_type == "any" then result_type = nil end
	local cache_str
	if type(result_type) == "string" then
		cache_str = query .. "&" .. result_type .. "&" .. language_id
	else
		cache_str = query .. "&nil&" .. language_id
	end

	local cache = match_query_cache[cache_str]
	if cache ~= nil then
		return unpack(cache)
	end

	cachemisses = cachemisses + 1
	
	if type(result_type) == "string" then
		-- for safety's sake... this might already be protected against
		-- elsewhere, but might as well here too.
		-- this gets rid of anything that isn't a letter or number and then
		-- condenses all whitespace to single spaces between words.
		result_type = result_type:gsub("[^%w%s_:]",""):gsub("%s+"," ")
		-- then get rid of leading or trailing spaces
		result_type = result_type:gsub("^%s*", ""):gsub("%s+$","")
		sqlquery = "SELECT m, function_id, matches.rule_id FROM matches, rules WHERE rules.language_id = "..language_id.." AND rules.rule_id = matches.rule_id AND (matchtype='"..result_type.."' or matchtype='any')"
--		debugp("sqlquery:",sqlquery)
	else
		sqlquery = "SELECT m, function_id, matches.rule_id FROM matches, rules WHERE rules.language_id = "..language_id.." AND rules.rule_id = matches.rule_id"
--		debugp("sqlquery:",sqlquery)
	end
	
	for match, function_id, rule_id in rows(con, sqlquery) do
--		debugp("x", match, result_type, function_id, rule_id)
		
		local matches = find_matches(query, match)
		
		for _, queries in ipairs(matches) do
			local i = 1
			local all_queries_match = true
			local subs = {}
			for _, matchtype in ipairs(matches.matchtypes) do
--				debugp("matchtype:", matchtype)
				-- if this is a special match just for use by the match function
				-- don't bother with the recursive checking.
				if matchtype:sub(1,1) ~= "_" then
--					debugp("in match: " .. match .. ", " .. rule_id .. " trying to match '" .. queries[i] .. "' with a %" .. get_matchtype_from_matchtype(matchtype) .. "%")
          new_language_id, new_matchtype = get_language_and_matchtype_from_matchtype(matchtype, language_id)
					matched, with_what = match_query(new_language_id, queries[i], new_matchtype)
					if matched then
						subs[matchtype] = with_what
					else
						-- if one query doesn't match it doesn't matter if the rest do or not.
--						debugp("all_queries_match = false")
						all_queries_match = false
						break
					end
				else
--					debugp("subs["..matchtype.."] = "..queries[i])
					subs[matchtype] = queries[i]
				end
				i = i + 1
			end
			
			-- if all of the subqueries matched, then return the result
			if all_queries_match then
				local exec = true
				local env = nil
				if function_id ~= nil and function_id ~= 0 then
					local vars = {}
					for i, matchtype in pairs(matches.matchtypes) do
            if matchtype:sub(1,1) == "_" then
							matchtype = matchtype:sub(2)
						end
						vars[get_varname_from_matchtype(matchtype)] = queries[i]
					end
					exec, env = get_function(function_id, vars)
--					debugp("exec: ", exec)
				end
				
				if exec then
					debugp(match .. " matches!", function_id, rule_id)
					local cur = con:execute("SELECT type, content FROM rules WHERE rule_id = '"..rule_id.."'")
					row = cur:fetch ({}, "a")
					table.insert(results, {rule = row, subs = subs, env = env})
--					print("result")
				end
			end
		end
 				
	end
-- 	
	if #results >= 1 then
		match_query_cache[cache_str] = {true, results}
		return true, results
	else
		match_query_cache[cache_str] = {false}
		return false
	end
end

function display_match(match, del, pre)
	if del == nil then del = "    " end
	if pre == nil then pre = "" end
	for _, amatch in pairs(match) do
		for k, v in pairs(amatch.rule) do
			print(pre .. k, v)
		end
		for matchtype, submatch in pairs(amatch.subs) do
			display_match(submatch, del, pre .. del)
		end
	end
end



function forwardto(url)
	return {type = "forwardto", url = url}
end

function isforwardto(data)
	return data.type == "forwardto"
end

-- executes the first match it sees in the tree.  The first subexpression in 
-- subs is always the only one visited.
function execute_first_match(match)
	local rule = match[1].rule
	if rule.type == "data" then
		return rule.content
	elseif rule.type == "query" then
		return rule.content
	elseif rule.type == "function" then
		-- TODO: cache the compiled code here if it is an issue.

		local env = match[1].env
		if not env then
			env = {os = {date = os.date, time = os.time}, 
						string = string, 
						tonumber = tonumber,
						print = print,
						table = table,
						math = math,
-- 						vars = {},
						pairs = pairs,
						ipairs = ipairs,
						forwardto = forwardto}
		end
		for k, v in pairs(exec_env) do
			env[k] = v
		end
		
		-- recur on submatches to get their values to bind in the environment
		for matchtype, submatch in pairs(match[1].subs) do
			if matchtype:sub(1,1) == "_" then
				matchtype = matchtype:sub(2)
-- 				env.vars[get_varname_from_matchtype(matchtype)] = submatch
				env[get_varname_from_matchtype(matchtype)] = submatch
			else
				local q = execute_first_match(submatch)
-- 				env.vars[get_varname_from_matchtype(matchtype)] = q
				env[get_varname_from_matchtype(matchtype)] = q
			end
		end
		
 		local f, err = loadstring(rule.content)
 		if type(f) ~= "function" then
 			error(err)
 		end
 		-- rule.exec = f
				
		setfenv(f, env)
		return f()
	elseif rule.type == "python" then
		pg = python.globals()
		python.execute("env = {}")
		
		-- recur on submatches to get their values to bind in the environment
		for matchtype, submatch in pairs(match[1].subs) do
			if matchtype:sub(1,1) == "_" then
				matchtype = matchtype:sub(2)
				pg.env[get_varname_from_matchtype(matchtype)] = submatch
			else
				local q = execute_first_match(submatch)
				pg.env[get_varname_from_matchtype(matchtype)] = q
			end
		end
		
		-- python.execute("env['__builtins__'] = None")
		-- pg.wrapper = "def __foo() :\n %s\n\n__ret = __foo()"
		pg.code = rule.content
-- 		python.execute("print wrapper % code.replace('\\r\\n', '\\n ')")
-- 		python.execute("exec wrapper % code.replace('\\r\\n', '\\n ') in env")
		python.execute("exec code.replace('\\r\\n', '\\n') in env")
		if pg.env.__ret then
			return pg.env.__ret
		else
			return "bah!"
		end
	else
		print(rule.type .. " is not a valid type")
	end
end


-- -- this code compiles all of the functions so they don't need to be later.
-- -- I like this idea, but a cache system should scale better
-- for _, rule in pairs(language) do
-- 	if rule.type == "function" then
-- 		local f, err = loadstring(rule.code)
-- 		if type(f) ~= "function" then
-- 			error(err)
-- 		end
-- 		rule.exec = f
-- 	end
-- end

function exec_query(language_id, query, matchtype)
    local matched, with_what = match_query(language_id, query, matchtype)
    -- if matched then display_match(with_what) end
    if matched then
    	return execute_first_match(with_what)
    end
end

-- here is where the execution starts.  Everything above is fn defns

exec_env.exec_query = exec_query

for instr in io.lines() do
	totalmatches = 0
	cachemisses = 0

	-- clean it up here for now ...
	instr = instr:gsub("%s+", " ")
	
	if instr == "debug" then
		debugp = print
	elseif instr == "debugoff" then
		debugp = function () end
	end
	
	local query
	local language = "english"
	xml = etree.fromstring(instr)
	for _, v in ipairs(xml) do
		if v.tag == "query" then
			query = v[1]
			query = query:gsub("^ ", "")
		elseif v.tag == "lastquery" then
			lastquery = v[1]
		elseif v.tag == "language" then
			language = v[1]
		end
	end
  
	con = sql:connect("nlp", "root", "badf00d")

  language_id = get_language_id(language)
  
	clear_sparql_cache()
	-- test to see if the combined match makes sesne first
	if lastquery == nil then lastquery = "" end

	combinedquery = lastquery .. " " .. query
	combinedquery = combinedquery:gsub("%s+", " ")
	combinedquery = combinedquery:gsub("^ ", "")
	local matched, with_what = match_query(language_id, combinedquery)
    -- if matched then display_match(with_what) end
	if not matched then
	    matched, with_what = match_query(language_id, query)
	else
		-- if it worked, this is the new query
		query = combinedquery
	end

	if matched then
		local ret, stylesheet = execute_first_match(with_what)
		local is, whynot = is_valid_query(ret)
		if is then
			if stylesheet == nil then
				stylesheet = ret.stylesheet
				if stylesheet == nil then
					stylesheet = "/english/xml-to-html.xsl"
				end
			end

			print("<?xml version='1.0' standalone='yes'?>")
			print("<results>")
			print("  <result>")
			print("    <query>")
			print("      <![CDATA[\n"..query_to_string(ret).."]]>")
			print("    </query>")
			print("    <stylesheet>"..stylesheet.."</stylesheet>")
			print("  </result>")
			print("  <matches>" .. #with_what.."<\/matches>")
			print("  <lastquery>"..query.."</lastquery>")
			print("  <totalmatches>"..totalmatches.."</totalmatches>")
			print("  <cachemisses>"..cachemisses.."</cachemisses>");
			print("</results>")
    elseif type(ret) == "number" then
      print(ret)
		elseif isforwardto(ret) then
			print("<?xml version='1.0' standalone='yes'?>")
			print("<results>")
			print("  <forwardto>"..ret.url.."</forwardto>")
			print("  <totalmatches>"..totalmatches.."</totalmatches>")
			print("  <cachemisses>"..cachemisses.."</cachemisses>");
			print("</results>")
		else
			local is, xml = pcall(etree.tostring, ret)
			if is then
				print(xml)
			else
				print(ret)
			end
		end
	else
-- 		print(query)
	end
--    print_sparql_cache()
end



