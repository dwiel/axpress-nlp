-- this file exposes the function find_matches(query, match)
-- query is any string
-- match is a string of the form "%anything% text %anything%"
--  this would match anything with " text " and atleast something
--  on either side.  %vars% will match to be atleast 1 charactor.
--  the text that matches the variables are returned in a list of 
--  possibilities.  Each possibility is a list of the text values
--      example:
--      find_matches("abcXYdefXYghYZijYZkl", "%a%XY%a%YZ%a%") returns
--      {{"abc", "defXYgh", "ijYZkl"},
--       {"abc", "defXYghYZij", "kl"},
--       {"abcXYdef", "gh", "ijYZkl"},
--       {"abcXYdef", "ghYZij", "kl"}}


function find_matches(query, match)
	-- ignore $'s for now because they fuck everything up.
	-- TODO: fix this the right way.  Right now the $s get eliminated, they
	-- shouldn't need to be.
	query = query:gsub("%$", "")
	match = match:gsub("%$", "")
	match = "^"..match.."$"

	-- used to split the match.  Copied directly from the lua wiki tutorial 
	-- about string manipulation/recipes
	local function Split(str, delim, maxNb)
	    -- Eliminate bad cases...
	    if string.find(str, delim) == nil then
	        return { str }
	    end
	    if maxNb == nil or maxNb < 1 then
	        maxNb = 0    -- No limit
	    end
	    local result = {}
	    local pat = "(.-)" .. delim .. "()"
	    local nb = 0
	    local lastPos
	    for part, pos in string.gfind(str, pat) do
	        nb = nb + 1
	        result[nb] = part
	        lastPos = pos
	        if nb == maxNb then break end
	    end
	    -- Handle the last field
	    if nb ~= maxNb then
	        result[nb + 1] = string.sub(str, lastPos)
	    end
	    return result
	end
	
	-- split the match to get an array of the strings between the matchtypes %%
	local strs = Split(match, "%%[%w%s_:]+%%")
	local matchtypes = {}
	for matchtype in match:gfind("%%([%w%s_:]+)%%") do
		table.insert(matchtypes, matchtype)
	end
	
	if #strs == 1 then
		if query:match(strs[1]) then
			return {matchtypes = matchtypes, {}}
		end
	end
	
	for i, S in ipairs(strs) do
		if i == 1 then
			-- don't % the initial ^
			strs[1] = "^"..strs[1]:sub(2,strs[1]:len()):gsub("(%p)", "%%%1")
		elseif i == #strs then
			-- don't % the ending $
			strs[i] = strs[i]:sub(1,strs[i]:len()-1):gsub("(%p)", "%%%1").."$" 
		else
			-- % 'em all
			strs[i] = strs[i]:gsub("(%p)", "%%%1")
		end
	end
	
	-- if there is a ^ all by itself to start, get rid of it
	if strs[1] == "^" then table.remove(strs, 1) end
	
	function copy(found_list)
		local ret = {}
		for k,v in ipairs(found_list) do
			ret[k] = v
		end
		return ret
	end
	
	function merge_found_list(dest, src)
		for _,v in ipairs(src) do
			table.insert(dest, v)
		end
		return dest
	end
	
	function string.real_len(str)
		return str:gsub("%%(%p)", "%1"):len()
	end
	
	-- found_list is a list of the parts of the query that have matched between strs
	-- before the current one.
	function find_matches_helper(query, found_list, pos)
		local results = {matchtypes = matchtypes}
		local S = strs[pos]
		if S == nil then print("S is nil ...") return results end
		-- loop through each occurrence of S in query
		local where = string.find(query, S..".*")
--		print(where, query, S..".*")
		while where ~= nil and where <= query:len() do
			-- we are going to take whatever is between 1 and where as a capture so
			-- it better not be an empty string
			if where ~= 1 then
				local left = string.sub(query, 1, where-1)
				local right = string.sub(query, where+S:real_len())
				table.insert(found_list, left)
--				print("lr", left, right)
				merge_found_list(results, find_matches_helper(right, found_list, pos+1))
				table.remove(found_list)
			else
				local left = string.sub(query, 1, where-1)
				local right = string.sub(query, where+S:real_len()-1)
--				print("lr", left, right)
				merge_found_list(results, find_matches_helper(right, found_list, pos+1))
			end
			where = string.find(query, S..".*", where+1)
--			print(where, query, S..".*")
		end
	
		local where = string.find(query, S)
--		print(where, query, S)
		-- if the last string isn't there, this was almost a match, but is not
		if where == nil then return results end
		-- if the last string is there, but there is nothing after it
		if where == 1 then return results end
		local last = string.sub(query, 1, where - 1)
		table.insert(found_list, last)
		if #found_list == #matchtypes then
	 		table.insert(results, copy(found_list))
	 	end
	 	table.remove(found_list)
	 	
	 	return results
	end
	
	return find_matches_helper(query, {}, 1)	
end

function print_found_list(list)
	if list == nil then
		print("tried to print a nil list")
		return
	end
	for _, found_list in ipairs(list) do
		local str = ""
		for _, v in ipairs(found_list) do
			str = str..v..", "
		end
		-- table.foreach(found_list, print)
		print(_, str:sub(1, str:len()-2))	
	end
	if list.matchtypes == nil then
		print("no matchtypes")
		return
	end
	for _, matchtype in ipairs(list.matchtypes) do
--		print("matchtype" .. _ .. ": '" .. matchtype .. "'")
	end
end

local function test()
	print("matches 4 combinations")
	local list = find_matches("abcXYdefXYghYZijYZkl", "%a%XY%a%YZ%a%")
	print_found_list(list)
	
	print("matches 2 combinations")
	local list = find_matches("XYdefXYghYZijYZkl", "%a%XY%a%YZ%a%")
	print_found_list(list)
	
	print("matches 2 combinations")
	local list = find_matches("XYdefXYghYZijYZkl", "XY%a%YZ%a%")
	print_found_list(list)
	
	print("matches nothing")
	local list = find_matches("abcXYdefXYghYZijYZkl", "%a%XY%a%YZ")
	print_found_list(list)
	
	print("matches nothing")
	local list = find_matches("abcXYXYdef", "%a%XY%a%XY%a%")
	print_found_list(list)
	
	print("matches {ab, c} and {a, bc}")
	local list = find_matches("abc", "%a%%a%")
	print_found_list(list)
	
	print("matches abc")
	local list = find_matches("XYabcZW", "XY%a%ZW")
	print_found_list(list)	
	
	print("matches, but no string output")
	local list = find_matches("abc", "abc")
	print_found_list(list)

	print("does not match")
	local list = find_matches("abcdef", "abc")
	print_found_list(list)
	
	print("matches anything")
	local list = find_matches("abdef", "%abc%")
	print_found_list(list)

	print("matches anything")
	local list = find_matches("abdef", "%_abc%")
	print_found_list(list)
	
	print("matches {'five', 'six'}")
	local list = find_matches("five + six", "%number:x% + %number:y%")
	print_found_list(list)
end

-- test()


-- <root><query>emails from about 3 weeks ago</query><lastquery>emails</lastquery></root>
-- <root><query>compose</query><lastquery>emails</lastquery></root>
-- <root><query>from lucas</query><lastquery>emails</lastquery></root>
-- <root><query>new email</query><lastquery>emails</lastquery></root>
-- <root><query>mom email</query><lastquery>emails</lastquery></root>
-- <root><query>email to mom</query><lastquery>emails</lastquery></root>
-- <root><query>compose to mom</query><lastquery>emails</lastquery></root>
-- <root><query>emails</query><lastquery>emails</lastquery></root>
-- <root><query>emails from sometime last week</query><lastquery>emails</lastquery></root>
-- <root><query>emails from sometime last week page 2</query><lastquery>emails</lastquery></root>
-- <root><query>show me all of my email from 3 weeks ago</query><lastquery>emails</lastquery></root>