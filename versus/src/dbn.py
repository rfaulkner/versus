"""
Module for learning source.
"""

from learn import HiddenLayer
from rbm import RBM

import theano
import theano.config as config
import theano.tensor as T
import theano.shared as shared

from theano.tensor.shared_randomstreams import RandomStreams


class DBN(object):
    """Deep Belief Network representation."""

    def __init__(self,
                 numpy_rng,
                 theano_rng=None,
                 n_ins=784,
                 hidden_layers_sizes=(500, 500),
                 n_outs=10):
        """This class is made to support a variable number of layers.

        :type numpy_rng: numpy.random.RandomState
        :param numpy_rng: numpy random number generator used to draw initial
                weights

        :type theano_rng: theano.tensor.shared_randomstreams.RandomStreams
        :param theano_rng: Theano random generator; if None is given one is
                       generated based on a seed drawn from `rng`

        :type n_ins: int
        :param n_ins: dimension of the input to the DBN

        :type n_layers_sizes: list of ints
        :param n_layers_sizes: intermediate layers size, must contain
                           at least one value

        :type n_outs: int
        :param n_outs: dimension of the output of the network
        """

        self.sigmoid_layers = []
        self.rbm_layers = []
        self.params = []
        self.n_layers = len(hidden_layers_sizes)
        self.numpy_rng = numpy_rng

        assert self.n_layers > 0

        if not theano_rng:
            theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))
        self.theano_rng = theano_rng

        # allocate symbolic variables for the data
        self.x = T.matrix('x')  # the data is presented as rasterized images
        self.y = T.ivector('y')  # the labels are presented as 1D vector of
                                 # [int] labels

    def train_layers(self, layers_sizes):
        """
        Method that iteratively trains the DBN layerwise
        """
        for i in xrange(self.n_layers):
            # construct the sigmoidal layer

            # the size of the input is either the number of hidden units of the
            # layer below or the input size if we are on the first layer
            if i == 0:
                input_size = layers_sizes[i - 1]

            # the input to this layer is either the activation of the hidden
            # layer below or the input of the DBN if you are on the first layer
            if i == 0:
                layer_input = self.x
            else:
                layer_input = self.sigmoid_layers[-1].output

            sigmoid_layer = HiddenLayer(rng=self.numpy_rng,
                                        _input=layer_input,
                                        n_in=input_size,
                                        n_out=layers_sizes[i],
                                        activation=T.nnet.sigmoid)

            # add the layer to our list of layers
            self.sigmoid_layers.append(sigmoid_layer)

            # its arguably a philosophical question...  but we are going to only declare that
            # the parameters of the sigmoid_layers are parameters of the DBN. The visible
            # biases in the RBM are parameters of those RBMs, but not of the DBN.
            self.params.extend(sigmoid_layer.params)

            # Construct an RBM that shared weights with this layer
            rbm_layer = RBM(numpy_rng=self.numpy_rng,
                            theano_rng=self.theano_rng,
                            _input=layer_input,
                            n_visible=input_size,
                            n_hidden=layers_sizes[i],
                            W=sigmoid_layer.W,
                            hbias=sigmoid_layer.b)
            self.rbm_layers.append(rbm_layer)

    def pretraining_functions(self, train_set_x, batch_size, k):
        ''' Generates a list of functions, for performing one step of gradient descent at a
        given layer. The function will require as input the minibatch index, and to train an
        RBM you just need to iterate, calling the corresponding function on all minibatch
        indexes.

        :type train_set_x: theano.tensor.TensorType
        :param train_set_x: Shared var. that contains all datapoints used for training the RBM
        :type batch_size: int
        :param batch_size: size of a [mini]batch
        :param k: number of Gibbs steps to do in CD-k / PCD-k
        '''

        # index to a [mini]batch
        index = T.lscalar('index')  # index to a minibatch

        learning_rate = T.scalar('lr')  # learning rate to use

        # number of batches
        n_batches = train_set_x.get_value(borrow=True).shape[0] / batch_size
        # begining of a batch, given `index`
        batch_begin = index * batch_size
        # ending of a batch given `index`
        batch_end = batch_begin + batch_size

        pretrain_fns = []
        for rbm in self.rbm_layers:

            # get the cost and the updates list
            # using CD-k here (persisent=None) for training each RBM.
            # TODO: change cost function to reconstruction error
            cost, updates = rbm.cd(learning_rate, persistent=None, k)

            # compile the Theano function; check if k is also a Theano
            # variable, if so added to the inputs of the function
            if isinstance(k, theano.Variable):
                inputs = [index, theano.Param(learning_rate, default=0.1), k]
            else:
                inputs =  [index, theano.Param(learning_rate, default=0.1)]
            fn = theano.function(inputs=inputs,
                                 outputs=cost,
                                 updates=updates,
                                 givens={self.x: train_set_x[batch_begin:
                                                             batch_end]})
            # append `fn` to the list of functions
            pretrain_fns.append(fn)

        return pretrain_fns

    def build_finetune_functions(self, datasets, batch_size, learning_rate):
        '''Generates a function `train` that implements one step of finetuning, a function
        `validate` that computes the error on a batch from the validation set, and a function
        `test` that computes the error on a batch from the testing set

        :type datasets: list of pairs of theano.tensor.TensorType
        :param datasets: It is a list that contain all the datasets;  the has to contain three
        pairs, `train`, `valid`, `test` in this order, where each pair is formed of two Theano
        variables, one for the datapoints, the other for the labels
        :type batch_size: int
        :param batch_size: size of a minibatch
        :type learning_rate: float
        :param learning_rate: learning rate used during finetune stage
        '''

        (train_set_x, train_set_y) = datasets[0]
        (valid_set_x, valid_set_y) = datasets[1]
        (test_set_x, test_set_y) = datasets[2]

        # compute number of minibatches for training, validation and testing
        n_valid_batches = valid_set_x.get_value(borrow=True).shape[0] / batch_size
        n_test_batches  = test_set_x.get_value(borrow=True).shape[0]  / batch_size

        index   = T.lscalar('index')    # index to a [mini]batch

        # compute the gradients with respect to the model parameters
        gparams = T.grad(self.finetune_cost, self.params)

        # compute list of fine-tuning updates
        updates = []
        for param, gparam in zip(self.params, gparams):
            updates.append((param, param - gparam * learning_rate))

        train_fn = theano.function(inputs=[index],
              outputs= self.finetune_cost,
              updates=updates,
              givens={
                self.x: train_set_x[index * batch_size: (index + 1) * batch_size],
                self.y: train_set_y[index * batch_size: (index + 1) * batch_size]})

        test_score_i = theano.function([index], self.errors,
                 givens={
                   self.x: test_set_x[index * batch_size: (index + 1) * batch_size],
                   self.y: test_set_y[index * batch_size: (index + 1) * batch_size]})

        valid_score_i = theano.function([index], self.errors,
              givens={
                 self.x: valid_set_x[index * batch_size: (index + 1) * batch_size],
                 self.y: valid_set_y[index * batch_size: (index + 1) * batch_size]})

        # Create a function that scans the entire validation set
        def valid_score():
            return [valid_score_i(i) for i in xrange(n_valid_batches)]

        # Create a function that scans the entire test set
        def test_score():
            return [test_score_i(i) for i in xrange(n_test_batches)]

        return train_fn, valid_score, test_score