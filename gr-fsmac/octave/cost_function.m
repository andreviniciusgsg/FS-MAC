function [J, grad] = cost_function (theta, x, y, alpha, lambda)
#
# Author: André Gomes, andre.gomes@dcc.ufmg.br - Federal University of Minas Gerais (UFMG), Brazil.
# 28/11/2017
#
	m = size(y, 1);
	x = [ones(m, 1) x];
	h = x*theta;

	J = (1/(2*m))*(sum(power(h-y, 2), 1) + lambda*sum(power(theta, 2), 1));
	grad = theta - (alpha/m)*((x'*(h - y)) + lambda*theta);
	grad(1) = theta(1) - (alpha/m)*(x(:, 1)'*(h - y));

endfunction
