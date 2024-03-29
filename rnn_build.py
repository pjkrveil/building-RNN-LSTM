import numpy as np
from rnn_utils import *

def rnn_cell_forward(xt, a_prev, parameters):
	"""
	Implements a single forward step of the RNN-cell as described in Figure (2)

	Arguments:
	xt -- your input data at timestep "t", numpy array of shape (n_x, m).
	a_prev -- Hidden state at timestep "t-1", numpy array of shape (n_a, m)
	parameters -- python dictionary containing:
	                    Wax -- Weight matrix multiplying the input, numpy array of shape (n_a, n_x)
	                    Waa -- Weight matrix multiplying the hidden state, numpy array of shape (n_a, n_a)
	                    Wya -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
	                    ba --  Bias, numpy array of shape (n_a, 1)
	                    by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
	Returns:
	a_next -- next hidden state, of shape (n_a, m)
	yt_pred -- prediction at timestep "t", numpy array of shape (n_y, m)
	cache -- tuple of values needed for the backward pass, contains (a_next, a_prev, xt, parameters)
	"""

	# Retrieve parameters from "parameters"
	Wax = parameters["Wax"]
	Waa = parameters["Waa"]
	Wya = parameters["Wya"]
	ba = parameters["ba"]
	by = parameters["by"]

	# compute next activation state using the formula given above
	a_next = np.tanh(np.matmul(Wax, xt) + np.matmul(Waa, a_prev) + ba)
	# compute output of the current cell using the formula given above
	yt_pred = softmax(np.matmul(Wya, a_next) + by)

	# store values you need for backward propagation in cache
	cache = (a_next, a_prev, xt, parameters)

	return a_next, yt_pred, cache


def rnn_forward(x, a0, parameters):
	"""
	Implement the forward propagation of the recurrent neural network described in Figure (3).

	Arguments:
	x -- Input data for every time-step, of shape (n_x, m, T_x).
	a0 -- Initial hidden state, of shape (n_a, m)
	parameters -- python dictionary containing:
	                    Waa -- Weight matrix multiplying the hidden state, numpy array of shape (n_a, n_a)
	                    Wax -- Weight matrix multiplying the input, numpy array of shape (n_a, n_x)
	                    Wya -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
	                    ba --  Bias numpy array of shape (n_a, 1)
	                    by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)

	Returns:
	a -- Hidden states for every time-step, numpy array of shape (n_a, m, T_x)
	y_pred -- Predictions for every time-step, numpy array of shape (n_y, m, T_x)
	caches -- tuple of values needed for the backward pass, contains (list of caches, x)
	"""

	# Initialize "caches" which will contain the list of all caches
	caches = []

	# Retrieve dimensions from shapes of x and parameters["Wya"]
	n_x, m, T_x = x.shape
	n_y, n_a = parameters["Wya"].shape

	# initialize "a" and "y" with zeros
	a = np.zeros((n_a, m, T_x))
	y_pred = np.zeros((n_y, m, T_x))

	# Initialize a_next
	a_next = a0

	# loop over all time-steps
	for t in range(T_x):
		# Update next hidden state, compute the prediction, get the cache
		a_next, yt_pred, cache = rnn_cell_forward(x[:,:,t], a_next, parameters)
		# Save the value of the new "next" hidden state in a
		a[:,:,t] = a_next
		# Save the value of the prediction in y
		y_pred[:,:,t] = yt_pred
		# Append "cache" to "caches"
		caches.append(cache)

	# store values needed for backward propagation in cache
	caches = (caches, x)

	return a, y_pred, caches


def lstm_cell_forward(xt, a_prev, c_prev, parameters):
	"""
	Implement a single forward step of the LSTM-cell as described in Figure (4)

	Arguments:
	xt -- your input data at timestep "t", numpy array of shape (n_x, m).
	a_prev -- Hidden state at timestep "t-1", numpy array of shape (n_a, m)
	c_prev -- Memory state at timestep "t-1", numpy array of shape (n_a, m)
	parameters -- python dictionary containing:
	                    Wf -- Weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
	                    bf -- Bias of the forget gate, numpy array of shape (n_a, 1)
	                    Wi -- Weight matrix of the update gate, numpy array of shape (n_a, n_a + n_x)
	                    bi -- Bias of the update gate, numpy array of shape (n_a, 1)
	                    Wc -- Weight matrix of the first "tanh", numpy array of shape (n_a, n_a + n_x)
	                    bc --  Bias of the first "tanh", numpy array of shape (n_a, 1)
	                    Wo -- Weight matrix of the output gate, numpy array of shape (n_a, n_a + n_x)
	                    bo --  Bias of the output gate, numpy array of shape (n_a, 1)
	                    Wy -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
	                    by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
	                    
	Returns:
	a_next -- next hidden state, of shape (n_a, m)
	c_next -- next memory state, of shape (n_a, m)
	yt_pred -- prediction at timestep "t", numpy array of shape (n_y, m)
	cache -- tuple of values needed for the backward pass, contains (a_next, c_next, a_prev, c_prev, xt, parameters)

	Note: ft/it/ot stand for the forget/update/output gates, cct stands for the candidate value (c tilde),
	      c stands for the memory value
	"""

	# Retrieve parameters from "parameters"
	Wf = parameters["Wf"]
	bf = parameters["bf"]
	Wi = parameters["Wi"]
	bi = parameters["bi"]
	Wc = parameters["Wc"]
	bc = parameters["bc"]
	Wo = parameters["Wo"]
	bo = parameters["bo"]
	Wy = parameters["Wy"]
	by = parameters["by"]

	# Retrieve dimensions from shapes of xt and Wy
	n_x, m = xt.shape
	n_y, n_a = Wy.shape

	# Concatenate a_prev and xt
	concat = np.zeros((n_a + n_x, m))
	concat[: n_a, :] = a_prev
	concat[n_a :, :] = xt

	# Compute values for ft, it, cct, c_next, ot, a_next using the formulas given figure (4)
	ft = sigmoid(np.matmul(Wf, concat) + bf)
	it = sigmoid(np.matmul(Wi, concat) + bi)
	cct = np.tanh(np.matmul(Wc, concat) + bc)
	c_next = ft * c_prev + it * cct
	ot = sigmoid(np.matmul(Wo, concat) + bo)
	a_next = ot * np.tanh(c_next)

	# Compute prediction of the LSTM cell
	yt_pred = softmax(np.matmul(Wy, a_next) + by)

	# store values needed for backward propagation in cache
	cache = (a_next, c_next, a_prev, c_prev, ft, it, cct, ot, xt, parameters)

	return a_next, c_next, yt_pred, cache


def lstm_forward(x, a0, parameters):
	"""
	Implement the forward propagation of the recurrent neural network using an LSTM-cell described in Figure (4).

	Arguments:
	x -- Input data for every time-step, of shape (n_x, m, T_x).
	a0 -- Initial hidden state, of shape (n_a, m)
	parameters -- python dictionary containing:
					    Wf -- Weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
					    bf -- Bias of the forget gate, numpy array of shape (n_a, 1)
					    Wi -- Weight matrix of the update gate, numpy array of shape (n_a, n_a + n_x)
					    bi -- Bias of the update gate, numpy array of shape (n_a, 1)
					    Wc -- Weight matrix of the first "tanh", numpy array of shape (n_a, n_a + n_x)
					    bc -- Bias of the first "tanh", numpy array of shape (n_a, 1)
					    Wo -- Weight matrix of the output gate, numpy array of shape (n_a, n_a + n_x)
					    bo -- Bias of the output gate, numpy array of shape (n_a, 1)
					    Wy -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
					    by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
	                    
	Returns:
	a -- Hidden states for every time-step, numpy array of shape (n_a, m, T_x)
	y -- Predictions for every time-step, numpy array of shape (n_y, m, T_x)
	caches -- tuple of values needed for the backward pass, contains (list of all the caches, x)
	"""

	# Initialize "caches", which will track the list of all the caches
	caches = []

	### START CODE HERE ###
	# Retrieve dimensions from shapes of x and parameters['Wy']
	n_x, m, T_x = x.shape
	n_y, n_a = parameters['Wy'].shape

	# initialize "a", "c" and "y" with zeros
	a = np.zeros((n_a, m, T_x))
	c = np.zeros((n_a, m, T_x))
	y = np.zeros((n_y, m, T_x))

	# Initialize a_next and c_next
	a_next = a0
	c_next = np.zeros(a_next.shape)

	# loop over all time-steps
	for t in range(T_x):
		# Update next hidden state, next memory state, compute the prediction, get the cache
		a_next, c_next, yt, cache = lstm_cell_forward(x[:,:,t], a_next, c_next, parameters)
		# Save the value of the new "next" hidden state in a
		a[:,:,t] = a_next
		# Save the value of the prediction in y
		y[:,:,t] = yt
		# Save the value of the next cell state
		c[:,:,t]  = c_next
		# Append the cache into caches
		caches.append(cache)

	# store values needed for backward propagation in cache
	caches = (caches, x)

	return a, y, c, caches


def rnn_cell_backward(da_next, cache):
	"""
	Implements the backward pass for the RNN-cell (single time-step).

	Arguments:
	da_next -- Gradient of loss with respect to next hidden state
	cache -- python dictionary containing useful values (output of rnn_cell_forward())

	Returns:
	gradients -- python dictionary containing:
					    dx -- Gradients of input data, of shape (n_x, m)
					    da_prev -- Gradients of previous hidden state, of shape (n_a, m)
					    dWax -- Gradients of input-to-hidden weights, of shape (n_a, n_x)
					    dWaa -- Gradients of hidden-to-hidden weights, of shape (n_a, n_a)
					    dba -- Gradients of bias vector, of shape (n_a, 1)
	"""

	# Retrieve values from cache
	(a_next, a_prev, xt, parameters) = cache

	# Retrieve values from parameters
	Wax = parameters["Wax"]
	Waa = parameters["Waa"]
	Wya = parameters["Wya"]
	ba = parameters["ba"]
	by = parameters["by"]

	# compute the gradient of tanh with respect to a_next
	dtanh = (1 - a_next ** 2) * da_next

	# compute the gradient of the loss with respect to Wax
	dxt = np.dot(Wax.T, dtanh)
	dWax = np.dot(dtanh, xt.T)

	# compute the gradient with respect to Waa
	da_prev = np.dot(Waa.T, dtanh)
	dWaa = np.dot(dtanh, a_prev.T)

	# compute the gradient with respect to b
	dba = np.sum(dtanh, axis = 1, keepdims = 1)

	# Store the gradients in a python dictionary
	gradients = {"dxt": dxt, "da_prev": da_prev, "dWax": dWax, "dWaa": dWaa, "dba": dba}

	return gradients


def rnn_backward(da, caches):
	"""
	Implement the backward pass for a RNN over an entire sequence of input data.

	Arguments:
	da -- Upstream gradients of all hidden states, of shape (n_a, m, T_x)
	caches -- tuple containing information from the forward pass (rnn_forward)

	Returns:
	gradients -- python dictionary containing:
					    dx -- Gradient w.r.t. the input data, numpy-array of shape (n_x, m, T_x)
					    da0 -- Gradient w.r.t the initial hidden state, numpy-array of shape (n_a, m)
					    dWax -- Gradient w.r.t the input's weight matrix, numpy-array of shape (n_a, n_x)
					    dWaa -- Gradient w.r.t the hidden state's weight matrix, numpy-arrayof shape (n_a, n_a)
					    dba -- Gradient w.r.t the bias, of shape (n_a, 1)
	"""
	    
	### START CODE HERE ###

	# Retrieve values from the first cache (t=1) of caches
	(caches, x) = caches
	(a1, a0, x1, parameters) = caches[0]

	# Retrieve dimensions from da's and x1's shapes
	n_a, m, T_x = da.shape
	n_x, m = x1.shape

	# initialize the gradients with the right sizes
	dx = np.zeros((n_x, m, T_x))
	dWax = np.zeros((n_a, n_x))
	dWaa = np.zeros((n_a, n_a))
	dba = np.zeros((n_a, 1))
	da0 = np.zeros((n_a, m))
	da_prevt = np.zeros((n_a, m))

	# Loop through all the time steps
	for t in reversed(range(T_x)):
		# Compute gradients at time step t. Choose wisely the "da_next" and the "cache" to use in the backward propagation step.
		gradients = rnn_cell_backward(da[:,:,t] + da_prevt, caches[t])
		# Retrieve derivatives from gradients
		dxt, da_prevt, dWaxt, dWaat, dbat = gradients["dxt"], gradients["da_prev"], gradients["dWax"], gradients["dWaa"], gradients["dba"]
		# Increment global derivatives w.r.t parameters by adding their derivative at time-step t
		dx[:, :, t] = dxt
		dWax += dWaxt
		dWaa += dWaat
		dba += dbat
	    
	# Set da0 to the gradient of a which has been backpropagated through all time-steps
	da0 = da_prevt

	# Store the gradients in a python dictionary
	gradients = {"dx": dx, "da0": da0, "dWax": dWax, "dWaa": dWaa,"dba": dba}

	return gradients


def lstm_cell_backward(da_next, dc_next, cache):
	"""
	Implement the backward pass for the LSTM-cell (single time-step).

	Arguments:
	da_next -- Gradients of next hidden state, of shape (n_a, m)
	dc_next -- Gradients of next cell state, of shape (n_a, m)
	cache -- cache storing information from the forward pass

	Returns:
	gradients -- python dictionary containing:
						dxt -- Gradient of input data at time-step t, of shape (n_x, m)
						da_prev -- Gradient w.r.t. the previous hidden state, numpy array of shape (n_a, m)
						dc_prev -- Gradient w.r.t. the previous memory state, of shape (n_a, m, T_x)
						dWf -- Gradient w.r.t. the weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
						dWi -- Gradient w.r.t. the weight matrix of the update gate, numpy array of shape (n_a, n_a + n_x)
						dWc -- Gradient w.r.t. the weight matrix of the memory gate, numpy array of shape (n_a, n_a + n_x)
						dWo -- Gradient w.r.t. the weight matrix of the output gate, numpy array of shape (n_a, n_a + n_x)
						dbf -- Gradient w.r.t. biases of the forget gate, of shape (n_a, 1)
						dbi -- Gradient w.r.t. biases of the update gate, of shape (n_a, 1)
						dbc -- Gradient w.r.t. biases of the memory gate, of shape (n_a, 1)
						dbo -- Gradient w.r.t. biases of the output gate, of shape (n_a, 1)
	"""

	# Retrieve information from "cache"
	(a_next, c_next, a_prev, c_prev, ft, it, cct, ot, xt, parameters) = cache

	### START CODE HERE ###
	# Retrieve dimensions from xt's and a_next's shape (≈2 lines)
	n_x, m = xt.shape
	n_a, m = a_next.shape

	# Compute gates related derivatives, you can find their values can be found by looking carefully at equations (7) to (10) (≈4 lines)
	dot = da_next * np.tanh(c_next) * ot * (1 - ot)
	dcct = (dc_next * it + ot * (1 - np.square(np.tanh(c_next))) * it * da_next) * (1 - np.square(cct))
	dit = (dc_next + da_next * ot * (1 - np.square(np.tanh(c_next)))) * cct * it * (1 - it)
	dft = (dc_next + da_next * ot * (1 - np.square(np.tanh(c_next)))) * c_prev * ft * (1 - ft)

	# Concatenate a_prev and xt
	concat = np.concatenate((a_prev, xt), axis = 0)

	# Compute parameters related derivatives. Use equations (11)-(14) (≈8 lines)
	dWf = np.dot(dft, concat.T)
	dWi = np.dot(dit, concat.T)
	dWc = np.dot(dcct, concat.T)
	dWo = np.dot(dot, concat.T)
	dbf = np.sum(dft, axis = 1, keepdims = True)
	dbi = np.sum(dit, axis = 1, keepdims = True)
	dbc = np.sum(dcct, axis = 1, keepdims = True)
	dbo = np.sum(dot, axis = 1, keepdims = True)

	# Call the parameters
	Wf = parameters["Wf"]
	Wi = parameters["Wi"]
	Wo = parameters["Wo"]
	Wc = parameters["Wc"]
	Wy = parameters["Wy"]
	bf = parameters["bf"]
	bi = parameters["bi"]
	bo = parameters["bo"]
	bc = parameters["bc"]
	by = parameters["by"]

	# Compute derivatives w.r.t previous hidden state, previous memory state and input. Use equations (15)-(17). (≈3 lines)
	da_prev = np.dot(Wf[:, :n_a].T, dft) + np.dot(Wi[:, :n_a].T, dit) + np.dot(Wc[:, :n_a].T, dcct) + np.dot(Wo[:, :n_a].T, dot)
	dc_prev = (dc_next + da_next * ot * (1 - np.square(np.tanh(c_next)))) * ft 
	dxt = np.dot(Wf[:, n_a:].T, dft) + np.dot(Wi[:, n_a:].T, dit) + np.dot(Wc[:, n_a:].T, dcct) + np.dot(Wo[:, n_a:].T, dot)

	"""
	da_prev = np.dot(parameters["Wf"][:, :n_a].T, dft) + ...
				np.dot(parameters["Wi"][:, :n_a].T, dit) + ...
				np.dot(parameters["Wc"][:, :n_a].T, dcct) + ...
				np.dot(parameters["Wo"][:, :n_a].T, dot)
	dc_prev = (dc_next + da_next * ot * (1 - np.square(np.tanh(c_next)))) * ft
	dxt = np.dot(parameters["Wf"][:, n_a:].T, dft) + ...
			np.dot(parameters["Wi"][:, n_a:].T, dit) + ...
			np.dot(parameters["Wc"][:, n_a:].T, dcct) + ...
			np.dot(parameters["Wo"][:, n_a:].T, dot)
	"""

	# Save gradients in dictionary
	gradients = {"dxt": dxt, "da_prev": da_prev, "dc_prev": dc_prev, "dWf": dWf,"dbf": dbf, "dWi": dWi,"dbi": dbi,
				"dWc": dWc,"dbc": dbc, "dWo": dWo,"dbo": dbo}

	return gradients


def lstm_backward(da, caches):
	"""
	Implement the backward pass for the RNN with LSTM-cell (over a whole sequence).

	Arguments:
	da -- Gradients w.r.t the hidden states, numpy-array of shape (n_a, m, T_x)
	caches -- cache storing information from the forward pass (lstm_forward)

	Returns:
	gradients -- python dictionary containing:
					    dx -- Gradient of inputs, of shape (n_x, m, T_x)
					    da0 -- Gradient w.r.t. the previous hidden state, numpy array of shape (n_a, m)
					    dWf -- Gradient w.r.t. the weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
					    dWi -- Gradient w.r.t. the weight matrix of the update gate, numpy array of shape (n_a, n_a + n_x)
					    dWc -- Gradient w.r.t. the weight matrix of the memory gate, numpy array of shape (n_a, n_a + n_x)
					    dWo -- Gradient w.r.t. the weight matrix of the save gate, numpy array of shape (n_a, n_a + n_x)
					    dbf -- Gradient w.r.t. biases of the forget gate, of shape (n_a, 1)
					    dbi -- Gradient w.r.t. biases of the update gate, of shape (n_a, 1)
					    dbc -- Gradient w.r.t. biases of the memory gate, of shape (n_a, 1)
					    dbo -- Gradient w.r.t. biases of the save gate, of shape (n_a, 1)
	"""

	# Retrieve values from the first cache (t=1) of caches.
	(caches, x) = caches
	(a1, c1, a0, c0, f1, i1, cc1, o1, x1, parameters) = caches[0]

	# Retrieve dimensions from da's and x1's shapes
	n_a, m, T_x = da.shape
	n_x, m = x1.shape

	# initialize the gradients with the right sizes
	dx = np.zeros((n_x, m, T_x))
	da0 = np.zeros((n_a, m))
	da_prevt = np.zeros(da0.shape)
	dc_prevt = np.zeros(da0.shape)
	dWf = np.zeros((n_a, n_a + n_x))
	dWi = np.zeros(dWf.shape)
	dWc = np.zeros(dWf.shape)
	dWo = np.zeros(dWf.shape)
	dbf = np.zeros((n_a, 1))
	dbi = np.zeros(dbf.shape)
	dbc = np.zeros(dbf.shape)
	dbo = np.zeros(dbf.shape)

	# loop back over the whole sequence
	for t in reversed(range(T_x)):
		# Compute all gradients using lstm_cell_backward
		gradients = lstm_cell_backward(da[:, :, t], dc_prevt, caches[t])

		# Store or add the gradient to the parameters' previous step's gradient
		dx[:,:,t] = gradients["dxt"]
		dWf += gradients["dWf"]
		dWi += gradients["dWi"]
		dWc += gradients["dWc"]
		dWo += gradients["dWo"]
		dbf += gradients["dbf"]
		dbi += gradients["dbi"]
		dbc += gradients["dbc"]
		dbo += gradients["dbo"]

	# Set the first activation's gradient to the backpropagated gradient da_prev.
	da0 = gradients["da_prev"]

	# Store the gradients in a python dictionary
	gradients = {"dx": dx, "da0": da0, "dWf": dWf,"dbf": dbf, "dWi": dWi,"dbi": dbi,
	            "dWc": dWc,"dbc": dbc, "dWo": dWo,"dbo": dbo}

	return gradients


def check_rnn_forward():
	### rnn_cell_forward
	"""
	a_next[4] =  [ 0.59584544  0.18141802  0.61311866  0.99808218  0.85016201  
					0.99980978	-0.18887155  0.99815551  0.6531151   0.82872037]
	a_next.shape =  (5, 10)
	yt_pred[1] = [ 0.9888161   0.01682021  0.21140899  0.36817467  0.98988387 
					0.88945212	0.36920224	0.9966312	0.9982559	0.17746526]
	yt_pred.shape =  (2, 10)
	"""
	print("\n\n##### [ rnn_cell_forward ] #####\n")

	np.random.seed(1)
	xt = np.random.randn(3,10)
	a_prev = np.random.randn(5,10)
	Waa = np.random.randn(5,5)
	Wax = np.random.randn(5,3)
	Wya = np.random.randn(2,5)
	ba = np.random.randn(5,1)
	by = np.random.randn(2,1)
	parameters = {"Waa": Waa, "Wax": Wax, "Wya": Wya, "ba": ba, "by": by}

	a_next, yt_pred, cache = rnn_cell_forward(xt, a_prev, parameters)
	print("a_next[4] = ", a_next[4])
	print("a_next.shape = ", a_next.shape)
	print("yt_pred[1] =", yt_pred[1])
	print("yt_pred.shape = ", yt_pred.shape)

	### rnn_forward
	"""
	a[4][1] =  [-0.99999375  0.77911235 -0.99861469 -0.99833267]
	a.shape =  (5, 10, 4)
	y_pred[1][3] = [ 0.79560373  0.86224861  0.11118257  0.81515947]
	y_pred.shape =  (2, 10, 4)
	caches[1][1][3] = [-1.1425182  -0.34934272 -0.20889423  0.58662319]
	len(caches) =  2
	"""
	print("\n\n##### [ rnn_forward ] #####\n")

	np.random.seed(1)
	x = np.random.randn(3,10,4)
	a0 = np.random.randn(5,10)
	Waa = np.random.randn(5,5)
	Wax = np.random.randn(5,3)
	Wya = np.random.randn(2,5)
	b = np.random.randn(5,1)
	by = np.random.randn(2,1)
	parameters = {"Waa": Waa, "Wax": Wax, "Wya": Wya, "ba": ba, "by": by}

	a, y_pred, caches = rnn_forward(x, a0, parameters)
	print("a[4][1] = ", a[4][1])
	print("a.shape = ", a.shape)
	print("y_pred[1][3] =", y_pred[1][3])
	print("y_pred.shape = ", y_pred.shape)
	print("caches[1][1][3] =", caches[1][1][3])
	print("len(caches) = ", len(caches))

def check_lstm_forward():
	### lstm_cell_forward
	"""
	a_next[4] =  [-0.66408471  0.0036921   0.02088357  0.22834167 -0.85575339
					0.00138482	0.76566531  0.34631421 -0.00215674  0.43827275]
	a_next.shape =  (5, 10)
	c_next[2] =  [ 0.63267805  1.00570849  0.35504474  0.20690913 -1.64566718
		0.11832942	0.76449811 -0.0981561  -0.74348425 -0.26810932]
	c_next.shape =  (5, 10)
	yt[1] = [ 0.79913913  0.15986619  0.22412122  0.15606108  0.97057211
				0.31146381	0.00943007  0.12666353  0.39380172  0.07828381]
	yt.shape =  (2, 10)
	cache[1][3] = [-0.16263996  1.03729328  0.72938082 -0.54101719  0.02752074
					-0.30821874	0.07651101 -1.03752894  1.41219977 -0.37647422]
	len(cache) =  10
	"""
	print("\n\n##### [ lstm_cell_forward ] #####\n")

	np.random.seed(1)
	xt = np.random.randn(3,10)
	a_prev = np.random.randn(5,10)
	c_prev = np.random.randn(5,10)
	Wf = np.random.randn(5, 5+3)
	bf = np.random.randn(5,1)
	Wi = np.random.randn(5, 5+3)
	bi = np.random.randn(5,1)
	Wo = np.random.randn(5, 5+3)
	bo = np.random.randn(5,1)
	Wc = np.random.randn(5, 5+3)
	bc = np.random.randn(5,1)
	Wy = np.random.randn(2,5)
	by = np.random.randn(2,1)

	parameters = {"Wf": Wf, "Wi": Wi, "Wo": Wo, "Wc": Wc, "Wy": Wy, "bf": bf, "bi": bi, "bo": bo, "bc": bc, "by": by}

	a_next, c_next, yt, cache = lstm_cell_forward(xt, a_prev, c_prev, parameters)
	print("a_next[4] = ", a_next[4])
	print("a_next.shape = ", c_next.shape)
	print("c_next[2] = ", c_next[2])
	print("c_next.shape = ", c_next.shape)
	print("yt[1] =", yt[1])
	print("yt.shape = ", yt.shape)
	print("cache[1][3] =", cache[1][3])
	print("len(cache) = ", len(cache))

	### lstm_forward
	"""
	a[4][3][6] =  0.172117767533
	a.shape =  (5, 10, 7)
	y[1][4][3] = 0.95087346185
	y.shape =  (2, 10, 7)
	caches[1][1[1]] = [ 0.82797464  0.23009474  0.76201118 -0.22232814
						-0.20075807  0.18656139	0.41005165]
	c[1][2][1] -0.855544916718
	len(caches) =  2
	"""
	print("\n\n##### [ lstm_forward ] #####\n")

	np.random.seed(1)
	x = np.random.randn(3,10,7)
	a0 = np.random.randn(5,10)
	Wf = np.random.randn(5, 5+3)
	bf = np.random.randn(5,1)
	Wi = np.random.randn(5, 5+3)
	bi = np.random.randn(5,1)
	Wo = np.random.randn(5, 5+3)
	bo = np.random.randn(5,1)
	Wc = np.random.randn(5, 5+3)
	bc = np.random.randn(5,1)
	Wy = np.random.randn(2,5)
	by = np.random.randn(2,1)

	parameters = {"Wf": Wf, "Wi": Wi, "Wo": Wo, "Wc": Wc, "Wy": Wy, "bf": bf, "bi": bi, "bo": bo, "bc": bc, "by": by}

	a, y, c, caches = lstm_forward(x, a0, parameters)
	print("a[4][3][6] = ", a[4][3][6])
	print("a.shape = ", a.shape)
	print("y[1][4][3] =", y[1][4][3])
	print("y.shape = ", y.shape)
	print("caches[1][1[1]] =", caches[1][1][1])
	print("c[1][2][1]", c[1][2][1])
	print("len(caches) = ", len(caches))

def check_rnn_backward():
	### rnn_cell_backward
	"""
	gradients["dxt"][1][2] = -0.460564103059
	gradients["dxt"].shape = (3, 10)
	gradients["da_prev"][2][3] = 0.0842968653807
	gradients["da_prev"].shape = (5, 10)
	gradients["dWax"][3][1] = 0.393081873922
	gradients["dWax"].shape = (5, 3)
	gradients["dWaa"][1][2] = -0.28483955787
	gradients["dWaa"].shape = (5, 5)
	gradients["dba"][4] = [ 0.80517166]
	gradients["dba"].shape = (5, 1)
	"""
	print("\n\n##### [ rnn_cell_backward ] #####\n")

	np.random.seed(1)
	xt = np.random.randn(3,10)
	a_prev = np.random.randn(5,10)
	Wax = np.random.randn(5,3)
	Waa = np.random.randn(5,5)
	Wya = np.random.randn(2,5)
	ba = np.random.randn(5,1)
	by = np.random.randn(2,1)
	parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "ba": ba, "by": by}

	a_next, yt, cache = rnn_cell_forward(xt, a_prev, parameters)

	da_next = np.random.randn(5,10)
	gradients = rnn_cell_backward(da_next, cache)
	print("gradients[\"dxt\"][1][2] =", gradients["dxt"][1][2])
	print("gradients[\"dxt\"].shape =", gradients["dxt"].shape)
	print("gradients[\"da_prev\"][2][3] =", gradients["da_prev"][2][3])
	print("gradients[\"da_prev\"].shape =", gradients["da_prev"].shape)
	print("gradients[\"dWax\"][3][1] =", gradients["dWax"][3][1])
	print("gradients[\"dWax\"].shape =", gradients["dWax"].shape)
	print("gradients[\"dWaa\"][1][2] =", gradients["dWaa"][1][2])
	print("gradients[\"dWaa\"].shape =", gradients["dWaa"].shape)
	print("gradients[\"dba\"][4] =", gradients["dba"][4])
	print("gradients[\"dba\"].shape =", gradients["dba"].shape)

	### rnn_backward
	"""
	gradients["dx"][1][2] = [-2.07101689 -0.59255627  0.02466855  0.01483317]
	gradients["dx"].shape = (3, 10, 4)
	gradients["da0"][2][3] = -0.314942375127
	gradients["da0"].shape = (5, 10)
	gradients["dWax"][3][1] = 11.2641044965
	gradients["dWax"].shape = (5, 3)
	gradients["dWaa"][1][2] = 2.30333312658
	gradients["dWaa"].shape = (5, 5)
	gradients["dba"][4] = [-0.74747722]
	gradients["dba"].shape = (5, 1)
	"""
	print("\n\n##### [ rnn_backward ] #####\n")

	np.random.seed(1)
	x = np.random.randn(3,10,4)
	a0 = np.random.randn(5,10)
	Wax = np.random.randn(5,3)
	Waa = np.random.randn(5,5)
	Wya = np.random.randn(2,5)
	ba = np.random.randn(5,1)
	by = np.random.randn(2,1)
	parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "ba": ba, "by": by}
	a, y, caches = rnn_forward(x, a0, parameters)
	da = np.random.randn(5, 10, 4)
	gradients = rnn_backward(da, caches)

	print("gradients[\"dx\"][1][2] =", gradients["dx"][1][2])
	print("gradients[\"dx\"].shape =", gradients["dx"].shape)
	print("gradients[\"da0\"][2][3] =", gradients["da0"][2][3])
	print("gradients[\"da0\"].shape =", gradients["da0"].shape)
	print("gradients[\"dWax\"][3][1] =", gradients["dWax"][3][1])
	print("gradients[\"dWax\"].shape =", gradients["dWax"].shape)
	print("gradients[\"dWaa\"][1][2] =", gradients["dWaa"][1][2])
	print("gradients[\"dWaa\"].shape =", gradients["dWaa"].shape)
	print("gradients[\"dba\"][4] =", gradients["dba"][4])
	print("gradients[\"dba\"].shape =", gradients["dba"].shape)	


def check_lstm_backward():
	### lstm_cell_backward
	"""
	gradients["dxt"][1][2] = 3.23055911511
	gradients["dxt"].shape = (3, 10)
	gradients["da_prev"][2][3] = -0.0639621419711
	gradients["da_prev"].shape = (5, 10)
	gradients["dc_prev"][2][3] = 0.797522038797
	gradients["dc_prev"].shape = (5, 10)
	gradients["dWf"][3][1] = -0.147954838164
	gradients["dWf"].shape = (5, 8)
	gradients["dWi"][1][2] = 1.05749805523
	gradients["dWi"].shape = (5, 8)
	gradients["dWc"][3][1] = 2.30456216369
	gradients["dWc"].shape = (5, 8)
	gradients["dWo"][1][2] = 0.331311595289
	gradients["dWo"].shape = (5, 8)
	gradients["dbf"][4] = [ 0.18864637]
	gradients["dbf"].shape = (5, 1)
	gradients["dbi"][4] = [-0.40142491]
	gradients["dbi"].shape = (5, 1)
	gradients["dbc"][4] = [ 0.25587763]
	gradients["dbc"].shape = (5, 1)
	gradients["dbo"][4] = [ 0.13893342]
	gradients["dbo"].shape = (5, 1)
	"""
	print("\n\n##### [ lstm_cell_backward ] #####\n")

	np.random.seed(1)
	xt = np.random.randn(3,10)
	a_prev = np.random.randn(5,10)
	c_prev = np.random.randn(5,10)
	Wf = np.random.randn(5, 5+3)
	bf = np.random.randn(5,1)
	Wi = np.random.randn(5, 5+3)
	bi = np.random.randn(5,1)
	Wo = np.random.randn(5, 5+3)
	bo = np.random.randn(5,1)
	Wc = np.random.randn(5, 5+3)
	bc = np.random.randn(5,1)
	Wy = np.random.randn(2,5)
	by = np.random.randn(2,1)

	parameters = {"Wf": Wf, "Wi": Wi, "Wo": Wo, "Wc": Wc, "Wy": Wy, "bf": bf, "bi": bi, "bo": bo, "bc": bc, "by": by}

	a_next, c_next, yt, cache = lstm_cell_forward(xt, a_prev, c_prev, parameters)

	da_next = np.random.randn(5,10)
	dc_next = np.random.randn(5,10)
	gradients = lstm_cell_backward(da_next, dc_next, cache)
	print("gradients[\"dxt\"][1][2] =", gradients["dxt"][1][2])
	print("gradients[\"dxt\"].shape =", gradients["dxt"].shape)
	print("gradients[\"da_prev\"][2][3] =", gradients["da_prev"][2][3])
	print("gradients[\"da_prev\"].shape =", gradients["da_prev"].shape)
	print("gradients[\"dc_prev\"][2][3] =", gradients["dc_prev"][2][3])
	print("gradients[\"dc_prev\"].shape =", gradients["dc_prev"].shape)
	print("gradients[\"dWf\"][3][1] =", gradients["dWf"][3][1])
	print("gradients[\"dWf\"].shape =", gradients["dWf"].shape)
	print("gradients[\"dWi\"][1][2] =", gradients["dWi"][1][2])
	print("gradients[\"dWi\"].shape =", gradients["dWi"].shape)
	print("gradients[\"dWc\"][3][1] =", gradients["dWc"][3][1])
	print("gradients[\"dWc\"].shape =", gradients["dWc"].shape)
	print("gradients[\"dWo\"][1][2] =", gradients["dWo"][1][2])
	print("gradients[\"dWo\"].shape =", gradients["dWo"].shape)
	print("gradients[\"dbf\"][4] =", gradients["dbf"][4])
	print("gradients[\"dbf\"].shape =", gradients["dbf"].shape)
	print("gradients[\"dbi\"][4] =", gradients["dbi"][4])
	print("gradients[\"dbi\"].shape =", gradients["dbi"].shape)
	print("gradients[\"dbc\"][4] =", gradients["dbc"][4])
	print("gradients[\"dbc\"].shape =", gradients["dbc"].shape)
	print("gradients[\"dbo\"][4] =", gradients["dbo"][4])
	print("gradients[\"dbo\"].shape =", gradients["dbo"].shape)

	### lstm_backward
	"""
	gradients["dx"][1][2] = [-0.00173313  0.08287442 -0.30545663 -0.43281115]
	gradients["dx"].shape = (3, 10, 4)
	gradients["da0"][2][3] = -0.095911501954
	gradients["da0"].shape = (5, 10)
	gradients["dWf"][3][1] = -0.0698198561274
	gradients["dWf"].shape = (5, 8)
	gradients["dWi"][1][2] = 0.102371820249
	gradients["dWi"].shape = (5, 8)
	gradients["dWc"][3][1] = -0.0624983794927
	gradients["dWc"].shape = (5, 8)
	gradients["dWo"][1][2] = 0.0484389131444
	gradients["dWo"].shape = (5, 8)
	gradients["dbf"][4] = [-0.0565788]
	gradients["dbf"].shape = (5, 1)
	gradients["dbi"][4] = [-0.15399065]
	gradients["dbi"].shape = (5, 1)
	gradients["dbc"][4] = [-0.29691142]
	gradients["dbc"].shape = (5, 1)
	gradients["dbo"][4] = [-0.29798344]
	gradients["dbo"].shape = (5, 1)
	"""
	print("\n\n##### [ lstm_backward ]#####\n")

	np.random.seed(1)
	x = np.random.randn(3,10,7)
	a0 = np.random.randn(5,10)
	Wf = np.random.randn(5, 5+3)
	bf = np.random.randn(5,1)
	Wi = np.random.randn(5, 5+3)
	bi = np.random.randn(5,1)
	Wo = np.random.randn(5, 5+3)
	bo = np.random.randn(5,1)
	Wc = np.random.randn(5, 5+3)
	bc = np.random.randn(5,1)

	parameters = {"Wf": Wf, "Wi": Wi, "Wo": Wo, "Wc": Wc, "Wy": Wy, "bf": bf, "bi": bi, "bo": bo, "bc": bc, "by": by}

	a, y, c, caches = lstm_forward(x, a0, parameters)

	da = np.random.randn(5, 10, 4)
	gradients = lstm_backward(da, caches)

	print("gradients[\"dx\"][1][2] =", gradients["dx"][1][2])
	print("gradients[\"dx\"].shape =", gradients["dx"].shape)
	print("gradients[\"da0\"][2][3] =", gradients["da0"][2][3])
	print("gradients[\"da0\"].shape =", gradients["da0"].shape)
	print("gradients[\"dWf\"][3][1] =", gradients["dWf"][3][1])
	print("gradients[\"dWf\"].shape =", gradients["dWf"].shape)
	print("gradients[\"dWi\"][1][2] =", gradients["dWi"][1][2])
	print("gradients[\"dWi\"].shape =", gradients["dWi"].shape)
	print("gradients[\"dWc\"][3][1] =", gradients["dWc"][3][1])
	print("gradients[\"dWc\"].shape =", gradients["dWc"].shape)
	print("gradients[\"dWo\"][1][2] =", gradients["dWo"][1][2])
	print("gradients[\"dWo\"].shape =", gradients["dWo"].shape)
	print("gradients[\"dbf\"][4] =", gradients["dbf"][4])
	print("gradients[\"dbf\"].shape =", gradients["dbf"].shape)
	print("gradients[\"dbi\"][4] =", gradients["dbi"][4])
	print("gradients[\"dbi\"].shape =", gradients["dbi"].shape)
	print("gradients[\"dbc\"][4] =", gradients["dbc"][4])
	print("gradients[\"dbc\"].shape =", gradients["dbc"].shape)
	print("gradients[\"dbo\"][4] =", gradients["dbo"][4])
	print("gradients[\"dbo\"].shape =", gradients["dbo"].shape)


def main():
	check_rnn_forward()

	check_lstm_forward()

	check_rnn_backward()

	check_lstm_backward()


if __name__ == '__main__':
	main()	