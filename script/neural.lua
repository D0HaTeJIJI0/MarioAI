socket = require("socket.core")
sock = socket.tcp()
sock:connect("127.0.0.1", 8080)

function perception()
  --Current screen (in level)
	local prevScr = memory.readbyte(0X071A)
	--Next screen (in level)
	local currScr = memory.readbyte(0X071B)
	--
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
	local s = {""}
	for i=1,#out do
		for j=1,#out[i] do
			s[#s+1] = out[i][j]
			s[#s+1] = " "
		end
	end
	s = table.concat(s)
	sock:send(s)
	controls = {}
	while true do
		local s = sock:receive("*l")
		if s == "0" then break end
		controls[s] = true
	end
	joypad.set(1, controls)
end
emu.registerafter(perception)