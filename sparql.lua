-- public: some functions that can be used by code executed in the grammar
exec_env = {}

--------------------------------------------------------------------------------
--
-- Function to build SPARQL tables
--
--------------------------------------------------------------------------------

function prefix(prefix, iri)
	local is_valid, why_not = is_valid_prefix(prefix)
	if not is_valid then
		error(why_not)
	end
	if type(iri) ~= "string" then
		error("iri must be a string")
	end
	return {prefixes = {[prefix] = iri}}
end


function where(subject, predicate, object)
	if is_valid_subject(subject) and
	   is_valid_predicate(predicate) and
	   is_valid_object(object) then
		return {wheres = {{type = "TRIPLE",
		                  subject = subject, 
		                  predicate = predicate,
		                  object = object}}}
	end
end

function filter(text)
	-- TODO: make sure this is a valid filter ...
	-- TODO: | at least make sure it is contained and won't cause problems with
	-- TODO: | other parts of the query.
	
	return {wheres = {{type = "FILTER", text = text}}}
end


function select(...)
	local selects = {}
	for _, v in pairs({...}) do
		if is_valid_var(v) then
			selects[v] = true
		end
	end
	
	return {selects = selects}
end


-- takes in either an order ("DESC" | "ASC") and a variable, or just a variable.
function orderby(x, y)
	if type(x) ~= "string" then
		return
	elseif is_valid_var(x) then
		return {orderby = {order = "ASC", var = x}}
	elseif (x == "DESC" or x == "ASC") and is_valid_var(y) then
		return {orderby = {order = x, var = y}}
	else
		return
	end
end


function limit(int)
	if type(int) ~= "number" then
		return
	end
	
	return {limit = math.floor(tonumber(int))}
end

function offset(int)
	if type(int) ~= "number" then
		return
	end
	
	return {offset = math.floor(tonumber(int))}
end

function stylesheet(style)
	if type(style) ~= "string" then
		return
	end
	
	return {stylesheet = style}
end

exec_env.prefix = prefix
exec_env.where = where
exec_env.filter = filter
exec_env.select = select
exec_env.limit = limit
exec_env.offset = offset
exec_env.orderby = orderby
exec_env.stylesheet = stylesheet



--------------------------------------------------------------------------------
--
-- Functions to merge, build and manipulate SPARQL tables
--
--------------------------------------------------------------------------------

function merge_list(l1, l2, insert)
	if l1 == nil then
		return l2
	elseif l2 == nil then
		return l1
	end
	
	local newlist = {}

	-- if insert wasn't supplied, use the table.insert.
	if insert == nil then insert = table.insert end
	
	for k, v in pairs(l1) do
		insert(newlist, k, v)
	end

	for k, v in pairs(l2) do
		insert(newlist, k, v)
	end
	
	return newlist
end


-- a safe insert that checks to make sure that the data structure remains valid
function insert_prefix(list, prefix, iri)
	-- print testing
	if type(list) ~= "table" then error("insert_prefix expected the list to be a table") end
	if not is_valid_prefix(prefix) then error(prefix .. " is not a valid prefix") end
	if type(iri) ~= "string" then error("expected new prefix to have a string iri, received a " .. type(iri)) end
	
--	if not list[prefix] then
--		list[prefix] = iri
--	end
	list[prefix] = iri
end


-- a safe insert checks for duplicate entries and invalid characters
function insert_select(list, var)
	if type(list) ~= "table" then error("insert_select expected the list to be a table") end
	if type(var) ~= "string" then error("insert_select expected the new var to be a string") end
	
	-- make sure that the variable has only alphanumeric characters
	-- it is easier to remove all question marks and then add one to the front
	var = "?" .. var:gsub("[^%w]", "")

	list[var] = true;
end



-- a safe insert for wheres.
-- there is really no use in trying to avoid duplicates here.  It is not worth
-- it at this point.  I don't think
function insert_where(list, _, where)
	if type(list) ~= "table" then error("insert_where expected the list to be a table", 2) end
	if not is_valid_where(where) then error("insert_where got an invalid where clause", 2) end
	
	table.insert(list, where)
	return list
end


-- does some testing.  
function merge_order_by(ob1, ob2)
	if type(ob2) == "table" then
		if type(ob1) == "table" then
			-- TODO: allow merging ORDER BY clauses, sort by the first then the
			-- TODO: | second.  Something like that anyway.
			
			return ob2
		end
		
		return ob2
	else
		if type(ob1) == "table" then
			return ob1
		else
			return nil
		end
	end
-- 	if type(ob1) ~= "table" then
-- 		if type(ob2) ~= "table" then
-- 			return nil
-- 		else
-- 			return ob2
-- 		end
-- 	else
-- 		if type(ob2) ~= "table" then
-- 			return ob1
-- 		end
-- 		
-- 		-- TODO: allow merging ORDER BY clauses, sort by the first then the
-- 		-- TODO: | second.  Something like that anyway.
-- 		
-- 		return ob1
-- 	end
end


-- converts i1 or i2 to a number
function merge_integer(i1, i2)
	i1 = tonumber(i1)
	i2 = tonumber(i2)
	
	if i2 == nil then
		if type(i1) == "number" then
			return math.floor(i1)
		else
			return nil
		end
	else
		if type(i2) == "number" then
			return math.floor(i2)
		else
			return nil
		end
	end
-- 	if i1 == nil then
-- 		if type(i2) == "number" then
-- 			return math.floor(i2)
-- 		else
-- 			return nil
-- 		end
-- 	else
-- 		if type(i1) == "number" then
-- 			return math.floor(i1)
-- 		else
-- 			return nil
-- 		end
-- 	end
end

function merge_boolean(b1, b2)
	if b2 == nil then
		if type(b1) == "boolean" then
			return b1
		else
			return nil
		end
	else
		if type(b2) == "boolean" then
			return b2
		else
			return nil
		end
	end
end

function merge_string(s1, s2)
	if s2 == nil then
		if type(s1) == "string" then
			return s1
		else
			return nil
		end
	else
		if type(s2) == "string" then
			return s2
		else
			return nil
		end
	end
end

-- warning: this function has side effects on q1.  Do not use it if this
-- is a problem.
function query_merge2(q1, q2)
	local q1_type = type(q1)
--	if q1_type == "string" then
--		q1 = parse_query(q1)
--	elseif q1_type ~= "table" then
	if q1_type ~= "table" then
		error("query_merge: q1 was passed as a " .. q1_type .. " instead of a table")
	end
	q1_type = nil
	
	local q2_type = type(q2)
--	if q2_type == "string" then
--		q2 = parse_query(q2)
--	elseif q2_type ~= "table" then
	if q2_type ~= "table" then
		print(debug.traceback())
		print(q2)
		error("query_merge: q2 was passed as a " .. q2_type .. " instead of a table")
	end
	q2_type = nil
	
	-- figure out what the resulting type is:
	local newtype
	local q1st = (type(q1.selects) == "table")
	local q2st = (type(q2.selects) == "table")
	if q2sr == true then
		newtype = "select"
	elseif q2.ask == true then
		newtype = "ask"
	elseif q2.ask == false then
		newtype = "select"
	elseif q1st == true then
		newtype = "select"
	elseif q1.ask == true then
		newtype = "ask"
	elseif q1.ask == false then
		newtype = "select"
	else
		newtype = nil
	end
	
	q1.prefixes = merge_list(q1.prefixes, q2.prefixes, insert_prefix)
	q1.selects = merge_list(q1.selects, q2.selects, insert_select)
	q1.wheres = merge_list(q1.wheres, q2.wheres, insert_where)
	q1.orderby = merge_order_by(q1.orderby, q2.orderby)
	q1.limit = merge_integer(q1.limit, q2.limit)
	q1.offset = merge_integer(q1.offset, q2.offset)
	q1.ask = merge_boolean(q1.ask, q2.ask)
	q1.stylesheet = merge_string(q1.stylesheet, q2.stylesheet)
	
	if newtype == "select" then
		q1.ask = nil
	elseif newtype == "ask" then
		q1.selects = nil
	elseif newtype == nil then
		-- do nothing
	end
	
	return q1
end

-- side effects q1 which is where the result is stored and what is returned
-- merge any number of queries, left to right
function query_merge(q1, ...)
	local q = q1
	for _, qn in pairs({...}) do
		q = query_merge2(q, qn)
	end
	
	return q
end

-- merge any number of queries, left to right, the result is a new query
function query_build(...)
	local q = {}
	for _, qn in pairs({...}) do
		q = query_merge2(q, qn)
	end
	
	return q
end

-- converts a query into an ask query
-- or returns a generic ask query that can be used in a query_build to make a
-- query an ask
function ask(q)
	if q == nil then
		return {ask = true}
	elseif type(q) == "table" then
		q.selects = nil
		q.ask = true
	end
end

exec_env.query_merge = query_merge
exec_env.query_build = query_build
exec_env.ask = ask




--------------------------------------------------------------------------------
--
-- Function to verify SPARQL tables are valid
--
--------------------------------------------------------------------------------

-- returns true if var is a valid variable name
function is_valid_var(var)
	if var:sub(1,1) ~= "?" then return false end
	var = var:sub(2)	-- remove the leading ?
	local newvar, numchanges = var:gsub("[^%w]", "")
	return numchanges == 0
end


function is_valid_subject(subject)
	-- TODO: this
	-- TODO: | is_valid_subject needs to be implemented
	
	return true
end


-- returns true if pred is a valid predicate
function is_valid_predicate(pred)
	return pred:match("%w+:%w+") or pred == "a"
end


-- returns true if obj is a valid object
function is_valid_object(obj)
	return is_valid_var(obj) or obj:match('"[^"]"') or is_valid_predicate(obj)
end


-- returns true if the input is a valid prefix
function is_valid_prefix(prefix)
	if type(prefix) ~= "string" then return false, "prefix not a string" end
	if prefix:match("%w+:") then
		return true
	else
		return false, "prefix must match '%w+:'"
	end
end

-- TODO: this could probably be a bit more restrictive
function is_valid_iri(iri)
	return type(iri) == "string"
end

-- returns true if where is a valid where clause
function is_valid_where(where)
	local where_type = type(where)
	if where_type == "string" then
		where_type = nil
		
		-- TODO: is_valid_where(type == "string")how to test this ...
		-- TODO: | need to test to make sure this isn't abused.
		
		return true
	elseif where_type == "table" then
		where_type = nil
		
		if where.type == "TRIPLE" then
			return	is_valid_var(where.subject) and 
					is_valid_predicate(where.predicate) and
					is_valid_object(where.object)
		elseif where.type == "FILTER" then
			return type(where.text) == "string"
		elseif where.type == "OPTIONAL" then
			return is_valid_where(where[1]) and is_valid_where(where[2])
		elseif where.type == "UNION" then
			return is_valid_where(where[1]) and is_valid_where(where[2])
		elseif where.type == "LIST" then
		
			-- if everything in the list is a where, so is this
			for _, v in pairs(where.list) do
				if not is_valid_where(v) then
					return false
				end
			end
			
			return true
		end
		
		return true
	else
		return false
	end
end


-- returns true if ob is a valid order by clause
function is_valid_order_by(ob)
	if type(ob) == "nil" then return true end
	if type(ob) ~= "table" then return false end

	local type_order = type(ob.order)
	if type_order == "string" then
		local order = ob.order:upper()
		if order ~= "DESC" and order ~= "ASC" then
			return false
		end
	elseif type_order ~= nil then
		return false
	end
	
	return is_valid_var(ob.var)
end

function is_valid_limit(limit)
	local type_limit = type(limit)
	if type_limit == "number" then
		return limit >= 0
	elseif type_limit == "nil" then
		return true
	else
		return false
	end
end

function is_valid_offset(offset)
	local type_offset = type(offset)
	if type_offset == "number" then
		return offset >= 0
	elseif type_offset == "nil" then
		return true
	else
		return false
	end
end

function is_valid_query(q)
	if type(q) ~= "table" then return false, "not a table" end
	
	if type(q.prefixes) == "table" then
		for prefix, iri in pairs(q.prefixes) do
			if not is_valid_prefix(prefix) then return false, "invalid prefix" end
			if not is_valid_iri(iri) then return false, "invalid iri" end
		end
	elseif type(q.prefixes) ~= "nil" then
		return false, "prefixes must be a table or nil"
	end
	
	if type(q.selects) == "table" then
		for var, _ in pairs(q.selects) do
			if not is_valid_var(var) then return false, "invalid var" end
		end
	elseif type(q.selects) ~= "nil" then
		return false, "selects must be a table or nil"
	end
	
	if type(q.wheres) == "table" then
		for _, where in pairs(q.wheres) do
			if not is_valid_where(where) then return false, "invalid where" end
		end
	elseif type(q.wheres) == "nil" then
		-- if this isn't a where then it must be an ask, or it isn't valid
		if type(q.ask) ~= "table" then
			return false, "query must be a where or an ask"
		end
	else
		return false, "wheres must be a table or nil"
	end
	
	if type(q.ask) ~= "boolean" and type(q.ask) ~= "nil" then
		return false, "ask must be a boolean or nil"
	end
	
	if type(q.stylesheet) ~= "string" and type(q.stylesheet) ~= "nil" then
		return false, "stylesheet must be a string or nil"
	end

	if not is_valid_order_by(q.orderby) then return false, "invalid order by" end
	if not is_valid_limit(q.limit) then return false, "invalid limit" end
	if not is_valid_offset(q.offset) then return false, "invalid offset" end
	
	return true
end



--------------------------------------------------------------------------------
--
-- Execute SPARQL queries
--
--------------------------------------------------------------------------------

function escape (s)
	s = string.gsub(s, "([%p%c])",
		function (c)
			return string.format("%%%02X", string.byte(c))
		end)
	s = string.gsub(s, " ", "+")
	return s
end

sparql_cache = {}

function clear_sparql_cache()
	sparql_cache = {}
	sparqlcalls = 0
	sparqlcachemisses = 0
end

function print_sparql_cache()
	print("sparqlcalls: ", sparqlcalls)
	print("sparqlcachemisses: ", sparqlcachemisses)
--	for query, response in pairs(sparql_cache) do
--		print("-------------------------")
--		print("query")
--		print(query)
--		print("response")
--		print(response)
--	end
end

function execute(q)
	if type(q) ~= "table" then return end

	sparqlcalls = sparqlcalls + 1
	
	local query = query_to_string(q)
	local escaped_query = escape(query)
	local cache = sparql_cache[query]
	if cache ~= nil then
		return cache
	end

	sparqlcachemisses = sparqlcachemisses + 1
	
	local rnd = os.time()
	if query ~= "" then
		local url = "http://localhost:2020/query?query="..escaped_query.."&stylesheet=/english/xml-to-html.xsl"
	
		require'socket.http'
		response_body = socket.http.request(url)
		sparql_cache[query] = response_body
	--	print(response_body)
	else	
		error("empty parse string")
	end
	
	return response_body
end

function ask_result(response)
	return response:match("true")
end

function parse(xml)

	local vars = {}
	
	-- get the variable names
	for varname in xml:gmatch('variable name="(%w+)"') do
		table.insert(vars, varname)
	end

	local results = {}	
	for result in xml:gmatch('<result>(.-)</result>') do
		local row = {}
		for varname, value in result:gmatch('<binding name="(%w+)">%s*<%w+>(.-)</%w+>%s*</binding>') do
			row[varname] = value
		end
		table.insert(results, row)
	end
	
	return results
end

exec_env.execute = execute
exec_env.ask_result = ask_result
exec_env.parse = parse

--------------------------------------------------------------------------------
--
-- Convert SPARQL tables to strings and back
--
--------------------------------------------------------------------------------



-- -- parses a string query and returs a valid query table
-- function parse_query(q)
-- 	-- TODO: this - not easy
-- end



function query_to_string(q)
	if type(q) ~= "table" then return "not a valid query" end
	
--	local s = "[["
	local s = ""
	
	if type(q.prefixes) == "table" then
		for prefix, iri in pairs(q.prefixes) do
			s = s .. "PREFIX " .. prefix .. " <" .. iri .. ">\n"
		end
	end
	
	if type(q.selects) == "table" then
		s = s .. "SELECT "
		for var, _ in pairs(q.selects) do
			s = s .. var .. " "
		end
		s = s .. "\n"
		s = s .. "WHERE {\n"
	elseif q.ask == true then
		s = s .. "ASK {\n"
	end
	
	if type(q.wheres) == "table" then
		for _, pattern in pairs(q.wheres) do
			if pattern.type == "TRIPLE" then
				s = s.."  "..pattern.subject.." "..pattern.predicate.." "..pattern.object.." . \n";
			elseif pattern.type == "FILTER" then
				s = s.."  FILTER( "..pattern.text.." ) . \n"
			end
		end
	end

	s = s .. "} ";

	if q.ask ~= true then	
		if type(q.orderby) == "table" then
			s = s.."ORDER BY "..q.orderby.order.."("..q.orderby.var..")\n"
		end
		
		if type(q.limit) == "number" then
			s = s.."LIMIT "..q.limit.."\n"
		end
		
		if type(q.offset) == "number" then
			s = s.."OFFSET "..q.offset.."\n"
		end
	end
		
--	s = s .. "]]"
	return s
end

exec_env.query_to_string = query_to_string


