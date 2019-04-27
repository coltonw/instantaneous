import time
import math
import random


def randomPolicy(state):
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    return state


class treeNode():
    def __init__(self, state, parent):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        self.totalReward = 0
        self.bestReward = float("-inf")
        self.bestTerminalState = None
        self.children = {}


class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        if timeLimit is not None:
            if iterationLimit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState):
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()

        else:
            for i in range(self.searchLimit):
                self.executeRound()

        bestChild = self.getBestChild(self.root, 0)
        return self.getAction(self.root, bestChild)

    def search_terminal_state(self, initialState):
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            rounds = 0
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                rounds += 1
                self.executeRound()
            print(f'rounds taken: {rounds}, rounds/s: {rounds / self.timeLimit * 1000}')
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        return self.getBestTerminalState(self.root, 0)

    def executeRound(self):
        node = self.selectNode(self.root)
        terminalState = self.rollout(node.state)
        reward = terminalState.getReward()
        self.backpropogate(node, reward, terminalState)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        for action in actions:
            if action not in node.children.keys():
                newNode = treeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def backpropogate(self, node, reward, terminalState):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            if node.bestReward < reward:
                node.bestReward = reward
                node.bestTerminalState = terminalState
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    def getBestTerminalState(self, node, explorationValue):
        bestValue = float("-inf")
        bestStates = []
        for child in node.children.values():
            if child.bestReward > bestValue:
                bestValue = child.bestReward
                bestStates = [child.bestTerminalState]
            elif child.bestReward == bestValue:
                bestStates.append(child.bestTerminalState)
        return random.choice(bestStates)

    def getAction(self, root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action
