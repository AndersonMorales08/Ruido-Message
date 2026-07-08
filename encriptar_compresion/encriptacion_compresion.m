function [secret, codigos, ky_pub, ky_pr, n] = encriptacion_compresion(mensaje)

    primos = [5003 5009 5011 5021 5023 5039 5051 5059 5077 5081 5087 5099 5101 ...
            5107 5113 5119 5147 5153 5167 5171 5179 5189 5197 5209 5227 5231 ...
            5233 5237 5261 5273 5279 5281 5297 5303 5309 5323 5333 5347 5351 ...
            5381 5387 5393 5399 5407 5413 5417 5419 5431 5437 5441 5443 5449 ...
            5471 5477 5479 5483 5501 5503 5507 5519 5521 5527 5531 5557 5563 ...
            5569 5573 5581 5591 5623 5639 5641 5647 5651 5653 5657 5659 5669 ...
            5683 5689 5693 5701 5711 5717 5737 5741 5743 5749 5779 5783 5791 ...
            5801 5807 5813 5821 5827 5839 5843 5849 5851 5857 5861 5867 5869 ...
            5879 5881 5897 5903 5923 5927 5939 5953 5981 5987];

    ascii_message = double(mensaje);

    [ascii_message_comprimido, codigos, ~, ~] = compresion_huffman.huffmanComprimir(ascii_message);
    % Bug 4 corregido: indexación clara para vector 1D
    num1 = primos(5);   % 5023
    num2 = primos(10);  % 5081
    [ky_pub, ky_pr, n] = encriptacion_rsa.def_rsa(num1, num2);
    %fprintf('Llave pública  (e=%d, n=%d)\n', ky_pub, n);
    %fprintf('Llave privada  (d=%d, n=%d)\n', ky_pr, n);
    
    % Cifrado
    secret = zeros(1, length(ascii_message_comprimido));
    for i = 1:length(ascii_message_comprimido)
        secret(i) = encriptacion_rsa.cifrado_rsa(ascii_message_comprimido(i), ky_pub, n);
    end
    
    %fprintf('Original  : %s\n', mensaje);
    %fprintf('Cifrado   : '); disp(secret);
end