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