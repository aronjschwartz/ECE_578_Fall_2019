#Program: Implements the Angel/Demon game with a quantum brain
#Author: Aron Schwartz
#Last edit: 10/18/2019
import sys
sys.path.append("../project_files/robot_drivers/")

from hex_walker_driver import *
import Adafruit_PCA9685
import time
import numpy as np
import SensorInput
import random
import cirq_test

#init the pwm stuffs and run selected tests
pwm_40= Adafruit_PCA9685.PCA9685(address=0x40)
pwm_41= Adafruit_PCA9685.PCA9685(address=0x41)

pwm_40.set_pwm_freq(60)
pwm_41.set_pwm_freq(60)

#create somee legs
rf = Leg(0, pwm_40, 0, 1, 2, 0)
rm = Leg(0, pwm_40, 3, 4, 5, 1)
rr = Leg(0, pwm_40, 6, 7, 8, 2)
lr = Leg(0, pwm_41, 0, 1, 2, 3)
lm = Leg(0, pwm_41, 6, 4, 5, 4)
lf = Leg(0, pwm_41, 3, 7, 8, 5)

#create the hex walker
hex_walker = Hex_Walker(rf, rm, rr, lr, lm, lf)

class angel_demon_game():

	def __init__(self, turns_max, hex_walker):

		#Angel variables
		self.angel_turn = 0
		self.angel_victory = False

		#Devil variables
		self.devil_victory = False

		#Hexapod variables
		self.hexapod_move = ""
		self.state = [0,0,0]
		#self.hex_walker = hex_walker

		#Game variables
		self.turn_num = 0
		self.max_turns = turns_max


		#Game board initialization
		self.game_width = 10
		self.game_height = 10
		self.game_grid = [["   " for x in range(self.game_width)] for y in range(self.game_height)]


		#Initialize the bomb position
		self.game_grid[0][7] = "BOMB"

		#Initialize the bot starting position
		self.game_grid[self.game_height - 1][0] = "BOT"


	#Function to clear the board
	def clear_board(self):
		for i in range(0, self.game_width):
			for j in range(0, self.game_height):
				self.game_grid[i][j] = " "

	#Function to move the bot up one square
	def move_board_bot_up(self):
		status = 0
		done = False
		for i in range(0, self.game_width):
			for j in range(0, self.game_height):
				if (self.game_grid[i][j] == "BOT"):
					if (i == 0): #Highest row, cant move up more
						status = 2
						done = True
						break
					else:
						try:
							self.game_grid[i][j] = "    "
							if (self.game_grid[i-1][j] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot
								self.game_grid[i-1][j] = "BOT"
								done = True
								break

						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to move the bot right one square
	def move_board_bot_right(self):
		status = 0
		done = False
		for i in range(0, self.game_width):
			for j in range(0, self.game_height):
				if (self.game_grid[i][j] == "BOT"):
					if (j == (self.game_width - 1)): #Farthest right, cant go more right
						status = 2
						done = True
						break
					else:
						try:
							self.game_grid[i][j] = "    "
							if (self.game_grid[i][j+1] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot
								self.game_grid[i][j+1] = "BOT"
								done = True
								break

						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to move the bot up-right one square
	def move_board_bot_up_right(self):
		status = 0
		done = False
		for i in range(0, self.game_width):
			for j in range(0, self.game_height):
				if (self.game_grid[i][j] == "BOT"):
					if ((i == 0) or (j == (self.game_width - 1))): #Either max height or far right, cant do up-right move
						status = 2
						done = True
						break
					else:
						try:
							self.game_grid[i][j] = "    "
							if (self.game_grid[i-1][j+1] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot
								self.game_grid[i-1][j+1] = "BOT"
								done = True
								break

						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to display the game board
	def show_game_board(self):
		print()
		print(np.matrix(self.game_grid))
		print()


	def angel_wins(self):
		print()
		print("THE ANGEL WINS!!!")
		print()

	def devil_wins(self):
		print()
		print("THE DEVIL WINS!!! BOOM!")
		print()

	def select_move_angel(self):
		choice = ""
		print("1 - No movement ")
		print("2 - Up ")
		choice = input("Enter choice: ")
		while(1):
			if (choice == "1"):
				choice = 1
				break
			elif (choice == "2"):
				choice = 2
				break
			else:
				print("Invalid choice")
				choice = input("Enter choice: ")
		return choice


	def select_move_devil(self):
		choice = ""
		print("1 - Right ")
		print("2 - Up-Right ")
		choice = input("Enter choice: ")
		while(1):
			if (choice == "1"):
				choice = 1
				break
			elif (choice == "2"):
				choice = 2
				break
			else:
				print("Invalid choice")
				choice = input("Enter choice: ")
		return choice



	def quantum_translate(self, state):
		move_code = cirq_test.run_circuit(state[0], state[1], state[2])
		return move_code

	def determine_state(self):
		vector = []
		vector = SensorInput.run_input()
		return vector

	def move_hexapod(self, move_code):
		if (move_code == "N"):
			print("No movement")

		elif (move_code == "UP"):
			print("Move up")
			hex_walker.walk(20, 0)
			time.sleep(0.1)
			hex_walker.rotate(1,LEFT) # correction
			time.sleep(0.1)
			hex_walker.walk(2,240)
			time.sleep(0.1)
			hex_walker.walk(1, 0)

		elif (move_code == "UR"):
			print("Move up right")
			hex_walker.walk(20, 0)
			time.sleep(0.1)
			hex_walker.rotate(1,LEFT) # correction
			time.sleep(0.1)
			hex_walker.walk(2,240)
			time.sleep(0.1)
			hex_walker.rotate(5, RIGHT)
			time.sleep(0.1)
			hex_walker.walk(20, 0)
			time.sleep(0.1)
			hex_walker.rotate(1,LEFT) # correction
			time.sleep(0.1)
			hex_walker.walk(2,240)
			time.sleep(0.1)
			hex_walker.rotate(5, LEFT)

		elif (move_code == "R"):
			print("Move right")
			hex_walker.rotate(5, RIGHT)
			time.sleep(0.1)
			hex_walker.walk(20, 0)
			time.sleep(0.1)
			hex_walker.rotate(1,LEFT) # correction
			time.sleep(0.1)
			hex_walker.walk(2,240)
			time.sleep(0.1)
			hex_walker.rotate(5,LEFT)

	def run_game(self):
		#Welcome message
		print("**************************************************************")
		print("*                                                            *")
		print("*       Welcome to the Angel-Devil QUANTUM robot game!       *")
		print("*                                                            *")
		print("**************************************************************")

		#Main game loop

		while(1):
			print("\n********* Starting turn ", self.turn_num, " **********\n")

			#Reset the move status (used to track if the move results in hitting the bomb)
			move_status = 0

			#Show the game board at the beginning of every turn

			#Check whos turn it is
			if (self.angel_turn == 1):
				print("***** Angels Turn *****")


				self.show_game_board()


				#Prompt user to select desired move
				move = self.select_move_angel()

				#Desired move is to do nothing
				if (move == 1):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]

					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Angel successfully tells bot to stay still")

					elif (quantum == 1):
						print("Angel disobeys neutrally and moves up!")
						move_status = self.move_board_bot_up()
						self.move_hexapod("UP")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Angel and moves right!")

						move_status = self.move_board_bot_right()
						self.move_hexapod("R")

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")



				#Desired move is to go up
				elif (move == 2):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Angel successfully tells bot to move up!")
						move_status = self.move_board_bot_up()
						self.move_hexapod("UP")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 1):
						print("Angel disobeys neutrally and stays still!")

					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Angel and moves up right!")

						move_status = self.move_board_bot_up_right()
						self.move_hexapod("UR")

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")

				self.angel_turn = 0
				self.turn_num +=1

				if (self.turn_num == self.max_turns):
					print("MAX TURNS REACHED, Angel wins!!")
					self.angel_victory = True
					break



			#Devils Turn
			elif(self.angel_turn == 0):
				print("****** Devils Turn *****")

				self.show_game_board()
				#Prompt user to select desired move
				move = self.select_move_devil()

				#Desired move is to move right
				if (move == 1):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]
					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Devil successfully tells bot to move right!")
						move_status = self.move_board_bot_right()
						self.move_hexapod("R")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 1):
						print("Devil disobeys neutrally and moves up-right!")
						move_status = self.move_board_bot_up_right()
						self.move_hexapod("UR")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Devil and moves up!")

						move_status = self.move_board_bot_up()
						self.move_hexapod("UP")

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")


				#Desired move to move up-right
				elif (move == 2):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]

					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Devil successfully tells bot to move up-right!")
						move_status = self.move_board_bot_up_right()
						self.move_hexapod("UR")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 1):
						print("Devil disobeys neutrally and moves right!")
						move_status = self.move_board_bot_right()
						self.move_hexapod("R")
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Devil and stays still!")


				self.angel_turn = 1
				self.turn_num +=1

				if (self.turn_num == self.max_turns):
					print("MAX TURNS REACHED, Angel wins!!")
					self.angel_victory = True
					break



		#If we break the loop and get here, check who won and execute the appropriate "victory" dance.  Could do left hand raise/right hand raise, etc
		if (self.angel_victory == True):
			self.angel_wins()

		elif (self.devil_victory == True):
			self.devil_wins()



def main():



	# create the #torso
#	r = Leg(0, pwm_41, 12, 11, 10, ARM_R)
#	l = Leg(0, pwm_40, 12, 11, 10, ARM_L)
#	rot = Rotator(0, pwm_40, 9)

	# Create instance of the game

	game = angel_demon_game(30, "test")


	game.run_game()


main()
