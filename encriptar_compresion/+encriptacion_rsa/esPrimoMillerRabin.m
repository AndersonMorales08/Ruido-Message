function esPrimo = esPrimoMillerRabin(n, k)
    if n < 2
        esPrimo = false; return;
    end
    primosPequenos = [2 3 5 7 11 13 17 19 23 29 31 37 41 43 47];
    if any(n == primosPequenos)
        esPrimo = true; return;
    end
    if any(mod(n, primosPequenos) == 0)
        esPrimo = false; return;
    end
 
    % Escribir n-1 = 2^r * d, con d impar
    d = n - 1;
    r = 0;
    while mod(d, 2) == 0
        d = d / 2;
        r = r + 1;
    end
 
    esPrimo = true;
    for i = 1:k
        a = randi([2, n-2]);
        x = encriptacion_rsa.modpow(a, d, n);
        if x == 1 || x == n-1
            continue;
        end
        compuesto = true;
        for j = 1:r-1
            x = encriptacion_rsa.modpow(x, 2, n);
            if x == n-1
                compuesto = false;
                break;
            end
        end
        if compuesto
            esPrimo = false;
            return;
        end
    end
end
