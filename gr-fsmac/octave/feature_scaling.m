function [y, u, s] = feature_scaling(x)
#
# Author: André Gomes, andre.gomes@dcc.ufmg.br - Federal University of Minas Gerais (UFMG), Brazil.
# 28/11/2017
#
	for k=1:size(x, 2)
		[vmax, imax] = max(x(:, k));
		[vmin, imin] = min(x(:, k));
		den = vmax - vmin;
		if den == 0
			den = 1;
		endif
		avg = mean(x(:, k));
		x(:, k) = (x(:, k) - avg)/den;
	endfor
	
	y = x;
	u = avg;
	s = den;

endfunction