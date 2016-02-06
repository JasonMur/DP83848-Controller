--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   12:36:38 01/15/2016
-- Design Name:   
-- Module Name:   
-- Project Name:  PhyTB
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: I2CMatrix
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
-- Notes: 
-- This testbench has been automatically generated using types std_logic and
-- std_logic_vector for the ports of the unit under test.  Xilinx recommends
-- that these types always be used for the top-level I/O of a design in order
-- to guarantee that the testbench will bind correctly to the post-implementation 
-- simulation model.
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--USE ieee.numeric_std.ALL;
 
ENTITY PhyTB IS
END PhyTB;
 
ARCHITECTURE behavior OF PhyTB IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT Phy
    PORT(
         MDIO : INOUT  std_logic;
         MDC : OUT  std_logic;
         fpgaClk : IN  std_logic;
         sda : INOUT  std_logic;
         sck : INOUT  std_logic;
         sdaTest : OUT  std_logic;
         sckTest : OUT  std_logic;
			BsyTest : OUT std_logic
        );
    END COMPONENT;
    

   --Inputs
SIGNAL MDIOSig, MDCSig, fpgaClkSig :  std_logic;
signal sckSig, sdaSig, BsySig : std_logic;
constant FPGACLOCKPERIOD : time := 10 ns; -- 50Mhz
constant I2CCLOCKPERIOD : time := 5 us; -- 100Kh0000z
signal writeSequence : std_logic_vector (35 downto 0);
signal MDIOSequence : std_logic_vector(32 downto 0);
signal bitCount : integer range 0 to 36;
signal readDataSig, writeDataSig, sdaTest, sckTest : std_logic;
signal regCount : integer range 0 to 8;
BEGIN

-- Component Instantiation
uut: Phy PORT MAP(
	MDIO => MDIOSig,
	MDC => MDCSig,
	fpgaClk => fpgaClkSig,
	sda => sdaSig,
	sck => sckSig,
	sdaTest => sdaTest,
	sckTest => sckTest,
	BsyTest => BsySig
	);

--  Test Bench Statements
clkProcess :process
begin
	fpgaClkSig <= '0';
   wait for FPGACLOCKPERIOD;
   fpgaClkSig <= '1';
   wait for FPGACLOCKPERIOD;
end process;
   
-- Stimulus process
stimProc: process
begin        
	
	bitCount <= 0;
	--I2C Start Signal
	wait for I2CCLOCKPERIOD;
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD/2;
	sckSig <= '0';
	wait for I2CCLOCKPERIOD/2;
	writeSequence <= "11000100Z00001000Z10101010Z01110110Z";  --
	wait for I2CCLOCKPERIOD/2;
	writeSingleReg: while bitCount <= 35 loop
		sdaSig <= writeSequence(35-bitCount);
		bitCount <= bitCount + 1;
		
		wait for I2CCLOCKPERIOD;
		sckSig <= '1';
		wait for I2CCLOCKPERIOD;
		sckSig <= '0';
		stretchClock: while BsySig = '1' loop
			wait for 1 ns;
		end loop stretchClock;
	end loop writeSingleReg;
	
	-- I2C Stop Signal
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD;
	sckSig <= '1';
	wait for I2CCLOCKPERIOD/2;
	sdaSig <= '1';
	
	writeSequence <= "11000100Z00000010Z10101010Z01100001Z";
	
	wait for I2CCLOCKPERIOD*5;
	bitCount <= 0;
	--I2C Start Signal
	wait for I2CCLOCKPERIOD;
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD/2;
	sckSig <= '0';
	wait for I2CCLOCKPERIOD;

--Write sequence Device Address, Register Address, 2 x Register Bytes
	writeSingleReg2: while bitCount <= 35 loop
		sdaSig <= writeSequence(35-bitCount);
		bitCount <= bitCount + 1;
		
		wait for I2CCLOCKPERIOD;
		sckSig <= '1';
		wait for I2CCLOCKPERIOD;
		sckSig <= '0';
		stretchClock1: while BsySig = '1' loop
			wait for 1 ns;
		end loop stretchClock1;
	end loop writeSingleReg2;
	
	regCount <= 0;
		
	writeMultipleReg: while regCount < 8 loop
		bitCount <= 18;
		wait for I2CCLOCKPERIOD/2;
		writeWord: while bitCount <= 35 loop
			sdaSig <= writeSequence(35-bitCount);
			bitCount <= bitCount + 1;
			
			wait for I2CCLOCKPERIOD;
			sckSig <= '1';
			wait for I2CCLOCKPERIOD;
			sckSig <= '0';
			stretchClock2: while BsySig = '1' loop
				wait for 1 ns;
			end loop stretchClock2;
		end loop writeWord;
		regCount <= regCount +1;
		writeSequence(8 downto 1) <= not (writeSequence(8 downto 1));
	end loop writeMultipleReg;
	
	-- I2C Stop Signal
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD;
	sckSig <= '1';
	wait for I2CCLOCKPERIOD/2;
	sdaSig <= '1';
	
	
	writeSequence <= "11000100Z00000010ZZZZZZZZZ0ZZZZZZZZ1";
	
	wait for I2CCLOCKPERIOD*5;
	bitCount <= 0;
	--I2C Start Signal
	wait for I2CCLOCKPERIOD;
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD/2;
	sckSig <= '0';
	wait for I2CCLOCKPERIOD;
--Write sequence Device Address, Register Address, 2 x Register Bytes
	readPreamble: while bitCount <= 17 loop
		sdaSig <= writeSequence(35-bitCount);
		bitCount <= bitCount + 1;
		
		wait for I2CCLOCKPERIOD;
		sckSig <= '1';
		wait for I2CCLOCKPERIOD;
		sckSig <= '0';
		stretchClock3: while BsySig = '1' loop
			wait for 1 ns;
		end loop stretchClock3;
	end loop readPreamble;
	
	-- I2C Stop Signal
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD;
	sckSig <= '1';
	wait for I2CCLOCKPERIOD/2;
	sdaSig <= '1';
	
	writeSequence <= "11000101ZZZZZZZZZ0ZZZZZZZZ1ZZZZZZZZ1";
	
	wait for I2CCLOCKPERIOD*5;
	bitCount <= 0;
	--I2C Start Signal
	wait for I2CCLOCKPERIOD;
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD/2;
	sckSig <= '0';
	wait for I2CCLOCKPERIOD;
--Write sequence Device Address, Register Address, 2 x Register Bytes
	readWord: while bitCount <= 26 loop
		sdaSig <= writeSequence(35-bitCount);
		bitCount <= bitCount + 1;
		
		wait for I2CCLOCKPERIOD;
		sckSig <= '1';
		wait for I2CCLOCKPERIOD;
		sckSig <= '0';
		stretchClock4: while BsySig = '1' loop
			wait for 1 ns;
		end loop stretchClock4;
	end loop readWord;
	
	-- I2C Stop Signal
	sdaSig <= '0';
	wait for I2CCLOCKPERIOD;
	sckSig <= '1';
	wait for I2CCLOCKPERIOD/2;
	sdaSig <= '1';
	
	
	wait;
end process;
--  End Test Bench 

 END;