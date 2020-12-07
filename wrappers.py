import math

# Fuck python again
# all my homies hate object
class Object(object):
	pass

class Coord:
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def toString(self):
		return "("+str(self.x)+","+str(self.y)+")"

class Wire:
	def __init__(self, coord1, coord2, startFacing, endFacing, width):
		self.start = coord1
		self.end = coord2
		self.startFacing = startFacing
		self.endFacing = endFacing
		global wireCounter # fml
		self.label = wireCounter = 1+wireCounter #  = wireCounter++

		self.width = width;

		if(not isinstance(coord2, Coord)):
			raise Exception("retard")

	def toString(self):
		return '''
		<comp lib="0" loc="('''+str(self.start.x)+','+str(self.start.y)+''')" name="Tunnel">
			<a name="facing" val="'''+str(self.startFacing)+'''"/>
		<a name="width" val="7"/>
			<a name="label" val="'''+str(self.label)+'''"/>
			<a name="width" val="'''+str(self.width)+'''"/>
		</comp>
		<comp lib="0" loc="('''+str(self.end.x)+','+str(self.end.y)+''')" name="Tunnel">
			<a name="facing" val="'''+str(self.endFacing)+'''"/>
		<a name="width" val="7"/>
			<a name="label" val="'''+str(self.label)+'''"/>
			<a name="width" val="'''+str(self.width)+'''"/>
		</comp>''' #'\n<wire from="('+str(self.start.x)+','+str(self.start.y)+')" to="('+str(self.end.x)+','+str(self.end.y)+')"/>'
class Mux:
	def __init__(self, x=0, y=0):
		self.pos = Coord(x, y)
		self.splitterPos = Coord(self.pos.x+20, self.pos.y+320) # Coord(self.pos.x + 20, self.pos.y + 320)

	def toString(self):
		return '''
		<comp lib="2" loc="('''+str(self.pos.x+40)+','+str(self.pos.y+160)+''')" name="Multiplexer">
		  <a name="select" val="5"/>
		  <a name="width" val="7"/>
		</comp>
		<comp lib="0" loc="('''+str(self.splitterPos.x)+','+str(self.splitterPos.y)+''')" name="Splitter">
	      <a name="facing" val="south"/>
	      <a name="fanout" val="5"/>
	      <a name="incoming" val="5"/>
	    </comp>'''

	def getHeight():
		return 350 # hopefully

	def getWidth():
		return 70 # hopefully

	def getSelectorCoords(self, n):
		return Coord(self.splitterPos.x + 10 + (4-n)*10, self.splitterPos.y + 20)

	def getInput(self, i):
		return Coord(self.pos.x, self.pos.y + i*10)

	def getOutputCoords(self):
		return Coord(self.pos.x+40, self.pos.y+160)

class Constant():
	def __init__(self, coord, value):
		self.pos = coord
		self.value = value # integer

	def toString(self):
		return '''
		<comp lib="0" loc="('''+str(self.pos.x)+','+str(self.pos.y)+''')" name="Constant">
			<a name="width" val="7"/>
			<a name="value" val="'''+hex(self.value)+'''"/>
		</comp>'''

class Circuit:
	def __init__(self):
		self.mux = [] # 2d array (layers of muxes)
		self.wires = []
		self.constants = CONSTANT
		self.circut = ""

	# get the number of mux layers and array of layer sizes for a given text input
	def getSizes(self, string):
		self.layerCount = math.ceil(math.log(len(string), 32))
		self.layerSizes = [2**(5*(self.layerCount - n - 1)) for n in range(self.layerCount)]
		return self.layerCount, self.layerSizes

	def fromString(self, string):
		layerCount, layerSizes = self.getSizes(string)

		# generate multiplexers
		self.mux = []
		for layerIndex in range(len(layerSizes)):
			layerArray = [Mux(MUX_START_X + layerIndex * (Mux.getWidth() + 70), MUX_START_Y + y * Mux.getHeight()) for y in range(layerSizes[layerIndex])]
			self.mux.append(layerArray)

		# connect multiplexers
		for layerI, currentLayer in enumerate(self.mux):
			for muxI, currentMux in enumerate(currentLayer):
				# connect mux selectors to counter pins
				for selectorI in range(5):
					self.wires.append(Wire(currentMux.getSelectorCoords(selectorI), COUNTER[layerI*5+selectorI], "north", "north", 1)) # HOPEFULLY: to bi znal delat

				if (layerI != len(self.mux)-1):
					# connect mux output to an input in the next layer
					nextMuxI = math.floor(muxI / 32)
					nextMuxInputI = muxI % 32
					self.wires.append(Wire(currentMux.getOutputCoords(), self.mux[layerI+1][nextMuxI].getInput(nextMuxInputI), "west", "east", 7))

		# connect first layer of muxes to constants
		for i, y in enumerate(string):
			muxI = math.floor(i / 32)
			inputI = i % 32
			print(muxI, inputI, CONSTANT[ord(y)].pos.toString(), self.mux[0][muxI].getInput(inputI).toString())

			self.wires.append(Wire(CONSTANT[ord(y)].pos, self.mux[0][muxI].getInput(inputI), "west", "east", 7))

		# connect last mux to output
		self.wires.append(Wire(self.mux[len(self.mux)-1][0].getOutputCoords(), TTY, "west", "east", 7));

		return self

	def toString(self):
		a = ""
		for layer in self.mux:
			for mux in layer:
				a += mux.toString()

		for wires in self.wires:
			a += wires.toString()

		for constants in self.constants:
			a += self.constants[constants].toString()

		with open(TEMPLATE_FILE, "r") as template:
			return template.read().replace(MAGIC_STRING, a)

	def save(self):
		with open(OUTPUT_FILE, "w") as out:
			out.write(self.toString())


TEMPLATE_FILE = "template.circ"
INPUT_FILE = "input.txt"
OUTPUT_FILE = "bee_movie.circ"
MAGIC_STRING = "This will have to be replaced by the actual content, DO NOT CHANGE!!!!!!!``"
TTY = Coord(10,720) # output coords
COUNTER = [Coord(180+(31-i)*10, 860) for i in range(32)] # coords of counter pins (LSB first)
#COUNTER = [Coord(180+i*10, 860) for i in range(32)] # coords of counter pins (MSB first)
CONSTANT = {} # coords of 7-bit character constants

MUX_START_Y = 940
MUX_START_X = 100

wireCounter = 0 # oh God

decoded = ""
with open(INPUT_FILE, "r") as input:
	decoded = input.read()

# generate constants
count = 0
for i in range(128):
	if chr(i) in decoded:
		CONSTANT[i] = Constant(Coord(20, MUX_START_Y+count*30), i)
		count+=1

# fuck python
# all my homies hate True
true = True
false = False



Circuit().fromString(decoded).save()
