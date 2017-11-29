function [opt_theta] = calculate_theta(x, y)
#
# Author: André Gomes, andre.gomes@dcc.ufmg.br - Federal University of Minas Gerais (UFMG), Brazil.
# 28/11/2017
#
	rows = size(x, 1);
	cols = size(x, 2) + 1;

	alpha0 = 0.01;
	lambda0 = 0;
	max_iter = 5000;

	theta0 = zeros(cols, 1);
	[opt_cost, opt_theta] = cost_function(theta0, x, y, alpha0, lambda0);

	opt_alpha = 0;
	opt_lambda = 0;

	for alpha=alpha0:5*alpha0:1
		for lambda=lambda0:.5:15
			for i=1:max_iter
				[cost, theta] = cost_function(opt_theta, x, y, alpha, lambda);
				if cost > opt_cost
					break;
				else			
					opt_cost = cost;
					opt_theta = theta;
					opt_alpha = alpha;
					opt_lambda = lambda;
				endif
			endfor
		endfor
	endfor

	printf("Opt alpha = %f, opt lambda = %f\n", opt_alpha, opt_lambda);

endfunction