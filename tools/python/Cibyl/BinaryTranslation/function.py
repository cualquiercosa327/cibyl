######################################################################
##
## Copyright (C) 2006,  Simon Kagstrom
##
## Filename:      function.py
## Author:        Simon Kagstrom <ska@bth.se>
## Description:   Function defs (inherits codeblock)
##
## $Id: function.py 13391 2007-02-02 12:26:28Z ska $
##
######################################################################
from sets import Set
from Cibyl.BinaryTranslation.codeblock import CodeBlock
from Cibyl.BinaryTranslation.basicblock import BasicBlock
from Cibyl import config
import Mips.instruction as instruction
import Mips.mips as mips

class Function(CodeBlock):
    """Container class for functions"""
    def __init__(self, controller, name, instructions, labels, trace=False):
	CodeBlock.__init__(self, controller, instructions, labels, trace)
	self.name = name
	self.basicBlocks = []

	# Assume this is a leaf function
	self.isLeafFunction = True

	# Create basic blocks and check leafness
	tmp = []
	for insn in self.instructions:
	    tmp.append(insn)
	    if insn.isBranch or insn.isBranchDestination and not insn.address == self.address:
		# Remove the last instruction if this is a branch -
		# but not for the function entry point. The reason is
		# that some functions might start with a branch
		if insn.isBranchDestination and not insn.address == self.address:
		    tmp = tmp[:-1]
		if tmp != []:
		    # Do not append empty basic blocks
		    bb = BasicBlock(self.controller, tmp, self.labels, trace)
		    self.basicBlocks.append(bb)
		tmp = []
		if insn.isBranchDestination and not insn.address == self.address:
		    tmp.append(insn)

	    if insn.isFunctionCall:
		self.isLeafFunction = False
            insn.setFunction(self)
	else:
	    # Last one
	    if tmp != []:
		self.basicBlocks.append(BasicBlock(self.controller, tmp, self.labels, trace))

	# Perform skip stack store optimization. We actually always do
	# this since we that way avoid zeroing registers unecessary
	if not config.debug:
	    self.doSkipStackStoreOptimization()

    def isLeaf(self):
	return self.isLeafFunction

    def getReturnBasicBlocks(self):
	out = []
	for bb in self.basicBlocks:
	    if bb.isReturnBlock:
		out.append(bb)
	return out

    def setJavaMethod(self, method):
	"Define which java method this instruction is in"
	self.javaMethod = method

    def getJavaMethod(self):
	"Return which java method this instruction is in"
	return self.javaMethod

    def doSkipStackStoreOptimization(self):
	"""Optimization to skip the stack saving and restoring since
	these are not actually needed with Cibyl (registers in local
	java variables)"""

	def instructionIsStackStore(insn):
	    return isinstance(insn, instruction.Sw) and insn.rt in mips.callerSavedRegisters and insn.rs == mips.R_SP

	def instructionIsStackLoad(insn):
	    return isinstance(insn, instruction.Lw) and insn.rt in mips.callerSavedRegisters and insn.rs == mips.R_SP

        for insn in self.basicBlocks[0].instructions:
            if instructionIsStackStore(insn):
                if config.verbose: print "Removing", insn
                insn.nullify()

        returnBasicBlocks = []
        returnBasicBlocks = returnBasicBlocks + self.getReturnBasicBlocks()
	for bb in returnBasicBlocks:
	    for insn in bb.instructions:
		# Validate that there is no use of the saved registers
		for dst in self.destinationRegisters:
		    if dst in mips.callerSavedRegisters and not instructionIsStackLoad(insn):
			return

	    for insn in bb.instructions:
		if instructionIsStackLoad(insn):
		    if config.verbose: print "Removing", insn
		    insn.nullify()

    def compile(self):
	"Compile this basic block to Java assembly"
	for bb in self.basicBlocks:
	    bb.compile()

    def __str__(self):
	out = "%s(%d):\n" % (self.name, self.getByteCodeSize())
	return out + CodeBlock.__str__(self)
