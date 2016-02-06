----------------------------------------------------------------------------------
-- Engineer: 				Jason Murphy
-- Create Date:   		09:00 01/27/2016 
-- Design Name: 			I2CInt
-- Module Name:   		I2CInt - Behavioral 
-- Project Name: 			Phy
-- Target Devices: 		Spartan 6 xc6slx9-3tgg144
-- Tool versions: 		ISE 14.7
-- Description: 			Simple I2C interface with 8 bit reg allowing 
--								multibyte read/write
--								Revision V1.1 now with Clock Stretching.
--								(When an external interface holds Bsy high
--								sck is held low to pause data transmission).
-- Dependencies: 			
-- Revision:				V1.1 "Clock Stretching" implemented
-- Revision: 				V1.0 Tested 
-- Revision 				0.01 - File Created
-- Additional Comments: 
----------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity I2CInt is port( 
	sda, sck : inout std_logic := 'Z';
	fpgaClk : in std_logic; 
	Bsy : in std_logic;	
	regAddr : out std_logic_vector (7 downto 0);
	regDataIn : in std_logic_vector (7 downto 0);
	regDataOut : out std_logic_vector (7 downto 0);
	readData, writeData : out std_logic := '1';
	sdaTest, sckTest : out std_logic);
end entity; 

architecture Behavioral of I2CInt is 
	constant thisDeviceAddr : std_logic_vector (6 downto 0) := "1100010"; --0x62
	signal sclReg, sdaReg : std_logic_vector (1 downto 0) := "11"; -- input debounce register 
	signal output, writeNotRead : std_logic := '1'; --default is writing data and output high
	signal bitCount : integer range 0 to 17 := 0; -- counting I2C bits read/written
	signal byteCount : integer range 0 to 3 := 0; -- counting I2C bytes read/written
	signal regAddrSig, inputBuff : std_logic_vector(7 downto 0); -- buffer for storing input bytes
	signal readDataSig : std_logic;
	signal incFLag : integer range 0 to 1;
begin
	process(fpgaClk) is
	begin
		if rising_edge(fpgaClk) then												
			sclReg <= sclReg(0) & sck; 					--debounce clock
			sdaReg <= sdaReg(0) & sda; 					--debounce data
			sdaTest <= sda;
			sckTest <= sck;
			if sclReg = "11" and sdaReg = "10" then	--On Start Event
				bitCount <= 0; 								--Reset bit count
			end if;

------------------Finite State Machine---------------------
			if sclReg = "01" then							--On rising edge sck
				writeData <= '1'; 							--Disable //ell write
				readData <= '1';								--Disable //ell read
				bitCount <= bitCount + 1; 					--Increment bit counter
				inputBuff <= inputBuff(6 downto 0) & sdaReg(1);		--continuously read serial data bits 
				if bitCount = 7 then 						--When the first data byte has been read
					if inputBuff(6 downto 0) = thisDeviceAddr then --For this device
						byteCount <= 1; 						--Increment the byte count
						writeNotRead <= not sdaReg(1); 	--Load read/write opcode
					else 											--If this is for another device addr
						bitCount <= 17;						--Set count state to Idle
						writeNotRead <= '1';					--Precautionary default write state
					end if;
				elsif bitCount = 8 then						--When Ack or Nack has been read
					if sdaReg(1) = '1' then    			--If NACK / end of data received
						bitCount <= 17;						--Set count state to Idle
						writeNotRead <= '1';					--Precautionary default write state
					else
						readData <= writeNotRead;			--Set read flag on read cycles
						if byteCount = 3 then				--On third (or greater) byte of write cycles
							writeData <= not (writeNotRead); 	--Set the Write flag
						end if;
					end if;
				elsif bitCount = 16 then 					--When another byte has been read 
					if writeNotRead = '1' then 			--And this is a write cycle
						if byteCount = 1 then 				--And this is the 2nd byte of data
							regAddrSig <= inputBuff(6 downto 0) & sdaReg(1);	--Get the register Address
							byteCount <= 2;  					--increment byte count
						elsif byteCount > 1 then 			--if this is a data byte (i.e. all subsequent bytes)
							regDataOut <= inputBuff(6 downto 0) & sdaReg(1);	--Load a byte of data to be written
							byteCount <= 3;					--increment byte count
						end if;
						if byteCount > 2 then 				--if this is a multiple byte write sequences			
							regAddrSig <= regAddrSig + 1; --increment the register address
						end if;
					else 											--If this is a read cycle
						regAddrSig <= regAddrSig + 1; 	--Increment register address for each byte read
						byteCount <= 2;
					end if;
					bitCount <= 8;		--set bit counter to loop back and process the next byte
				end if;
			end if;
-------------------------------------------------------------------------

-----------------Clock Stretching and new output generation--------------
			if sclReg = "00" then 							--When the clock is already low
				sda <= 'Z';										--Default data high impedance 
				if Bsy = '1' then								--If external interface is busy
					sck <= '0';									--Keep the clock low (stretch clock)
				else												--If not
					sck <= 'Z';									--Set to high impedance (enable clock)
					if bitCount = 8 then 					--at the Ack/Nack bit
						if writeNotRead = '1' or byteCount = 1 then	--on all bytes during Write cycles or first byte of a read cycle
							sda <= '0'; 						--send an ACK signal
						end if;
					elsif bitCount > 8 and bitCount < 17 then						--On all subsequent bytes
						if (regDataIn(16-bitCount) or writeNotRead) = '0' then	--For read cycles, if a '0' has been read
							sda <= '0';							--output it!
						end if;
					end if;
				end if;
			end if;
-------------------------------------------------------------------------
		end if;
	end process;
	regAddr <= regAddrSig; 				--Write the reg addr to the output (using a signal allows address increment)
end Behavioral;


