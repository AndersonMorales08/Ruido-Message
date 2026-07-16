function p = generador_primos(bits)
    encontrado = false;
    low  = 2^(bits-1);
    high = 2^bits - 1;
    while ~encontrado
        candidato = randi([low, high]);
        candidato = bitor(candidato, 1); % asegurar que sea impar
        if encriptacion_rsa.esPrimoMillerRabin(candidato, 20)
            p = candidato;
            encontrado = true;
        end
    end
end
