% =========== Elevar exponente sin desbordamiento ===========
function result = modpow(base, exponent, modulus)
    result = 1;
    base = mod(base, modulus);
    while exponent > 0
        if mod(exponent, 2) == 1
            result = mod(result * base, modulus);
        end
        exponent = floor(exponent / 2);
        base = mod(base * base, modulus);
    end
end

% =========== Calcula e, d, n ===========
function [e, d, n] = def_rsa(nump1, nump2)
    candidatos_e = [5087 5099 5101 5107 5113 5119 5147 5153 5167 5171 ...
                    5179 5189 5197 5209 5227];
    n   = nump1 * nump2;
    phi = (nump1 - 1) * (nump2 - 1);

    e = 0;
    for pr = candidatos_e
        if pr < phi && gcd(pr, phi) == 1
            e = pr;
            break;
        end
    end
    if e == 0
        error('Ningún candidato es coprimo con phi. Usa otros primos.');
    end

    % Inverso modular de e (d·e ≡ 1 mod phi)
    [~, x, ~] = gcd(e, phi);
    d = mod(x, phi);
end

function c = cifrado_rsa(m, e, n)
    c = modpow(m, e, n);   % ✅ sin desbordamiento
end

function m_rec = descifrado_rsa(c, d, n)
    m_rec = modpow(c, d, n);   % ✅ sin desbordamiento
end


primos = [5003 5009 5011 5021 5023 5039 5051 5059 5077 5081 5087 5099 5101 ...
          5107 5113 5119 5147 5153 5167 5171 5179 5189 5197 5209 5227 5231 ...
          5233 5237 5261 5273 5279 5281 5297 5303 5309 5323 5333 5347 5351 ...
          5381 5387 5393 5399 5407 5413 5417 5419 5431 5437 5441 5443 5449 ...
          5471 5477 5479 5483 5501 5503 5507 5519 5521 5527 5531 5557 5563 ...
          5569 5573 5581 5591 5623 5639 5641 5647 5651 5653 5657 5659 5669 ...
          5683 5689 5693 5701 5711 5717 5737 5741 5743 5749 5779 5783 5791 ...
          5801 5807 5813 5821 5827 5839 5843 5849 5851 5857 5861 5867 5869 ...
          5879 5881 5897 5903 5923 5927 5939 5953 5981 5987];

mensaje = 'Hola';
ascii_message = double(mensaje);

% Bug 4 corregido: indexación clara para vector 1D
num1 = primos(5);   % 5023
num2 = primos(10);  % 5081

[e, d, n] = def_rsa(num1, num2);
fprintf('Llave pública  (e=%d, n=%d)\n', e, n);
fprintf('Llave privada  (d=%d, n=%d)\n', d, n);

% Cifrado
secret = zeros(1, length(ascii_message));
for i = 1:length(ascii_message)
    secret(i) = cifrado_rsa(ascii_message(i), e, n);
end

% ✅ Bug 3 corregido: descifrar antes de convertir a char
recovered_ascii = zeros(1, length(secret));
for i = 1:length(secret)
    recovered_ascii(i) = descifrado_rsa(secret(i), d, n);
end

fprintf('Original  : %s\n', mensaje);
fprintf('Cifrado   : '); disp(secret);
fprintf('Descifrado: %s\n', char(recovered_ascii));