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