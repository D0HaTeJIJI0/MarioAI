function setControls()
	local file = io.open ("controlls.txt", "r")
	local controller = {}
	if file then 
		for line in file:lines() do
			local key, value = unpack(line:split(" "))
			controller[key] = value
		end
	end
	joypad.set(1, controller)	
end
function perception()
	local prevScr = memory.readbyte(0X071A)
	local currScr = memory.readbyte(0X071B)
	local edge = memory.readbyte(0X71D)
	local prevScrStart = 0x500 + (prevScr % 2) * 0xD0 + (edge + (currScr - prevScr)) / 0x10
	local prevScrEnd = 0x50F + (prevScr % 2) * 0xD0
	local currScrStart = 0x500 + (currScr % 2) * 0xD0
	local currScrEnd = 0x500 + (currScr % 2) * 0xD0 + edge / 0x10
	local out = {}
	for row = 0, 12 do 
		out[row] = {}
		local j = 0
		local currTile = prevScrStart
		while currTile <= prevScrEnd do
			out[row][j] = 0
			local value = memory.readbyte(currTile)
			if (value ~= 0 and value ~= 0xC2) then
				out[row][j] = 1
			end			
			currTile = currTile + 1
			j = j + 1
		end
		local currTile = currScrStart
		prevScrStart = prevScrStart + 0x10
		prevScrEnd = prevScrEnd + 0x10
		while currTile <= currScrEnd do
			out[row][j] = 0
			local value = memory.readbyte(currTile)
			if (value ~= 0 and value ~= 0xC2) then
				out[row][j] = 1
			end			
			currTile = currTile + 1
			j = j + 1
		end
		currScrStart = currScrStart + 0x10
		currScrEnd = currScrEnd + 0x10
	end
	local marioY = math.floor(memory.readbyte(0x03B8) / 15)
	if (marioY > 0 and marioY < 13) then
		local marioX = math.floor(memory.readbyte(0x03AD) / 15)
		out[marioY-1][marioX] = 2
		if (memory.readbyte(0x0754) == 0 and marioY > 1) then
			out[marioY-2][marioX] = 2
		end
	end
    for slot = 0, 4 do
		local enemy = memory.readbyte(0xF + slot)
		if enemy ~= 0 then
			enemyX = math.floor(memory.readbyte(0x04B0 + slot * 4) / 16)
			enemyY = math.floor(memory.readbyte(0x04B1 + slot * 4) / 16)
			--if (enemyY >= 0 and enemyY < 12) and (enemyX >= 0 and enemyX <= 15) then
			--	out[enemyY - 2][enemyX] = -1
			--end
		end
	end	
	local file = io.open ("out.txt", "w")
	io.output(file)
	for i = 0, 12 do
		for j = 0, 15 do 
			io.write(string.format("%2d", out[i][j]))
		end
		io.write("\n")
	end
	io.close(file)
		local file = io.open ("controlls.txt", "r")
	--local controller = {}
	--if file then 
	--	for line in file:lines() do
	--		local key = line
	--		controller[key] = true
	--	end
	--end
	--joypad.set(1, controller)
end
emu.registerafter(perception)