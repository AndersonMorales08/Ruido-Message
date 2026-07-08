function [bitsComprimidos, codigos, entropia, longitudPromedio] = huffmanComprimir(datos)
% HUFFMANCOMPRIMIR Comprime un vector de datos usando codificación de Huffman
%
% Basado en la teoría de la información de Shannon: construye un código
% de prefijo óptimo que asigna códigos más cortos a los símbolos más
% frecuentes, acercándose al límite teórico de la entropía H(X).
%
% ENTRADAS:
%   datos - vector de enteros (p.ej. valores ASCII/uint8 de un mensaje)
%
% SALIDAS:
%   bitsComprimidos   - vector de bits (0/1) con la secuencia comprimida
%   codigos           - containers.Map: simbolo -> código binario (string)
%   entropia          - entropía de Shannon H(X) en bits/símbolo
%   longitudPromedio  - longitud promedio real del código Huffman (bits/símbolo)

    datos = double(datos(:)'); % vector fila de tipo double

    % 1. Distribución de probabilidad empírica de la fuente
    simbolosUnicos = unique(datos);
    n = numel(datos);
    probabilidades = zeros(size(simbolosUnicos));
    for i = 1:numel(simbolosUnicos)
        probabilidades(i) = sum(datos == simbolosUnicos(i)) / n;
    end

    % 2. Entropía de Shannon: H(X) = -sum(p*log2(p))
    entropia = -sum(probabilidades .* log2(probabilidades));

    % 3. Construir el árbol de Huffman y obtener el diccionario de códigos
    codigos = compresion_huffman.construirArbol(simbolosUnicos, probabilidades);

    % 4. Codificar concatenando el código de cada símbolo
    bitsCell = cell(1, n);
    for i = 1:n
        bitsCell{i} = codigos(datos(i));
    end
    cadenaBits = [bitsCell{:}];
    bitsComprimidos = cadenaBits - '0'; % char '0'/'1' -> vector numérico

    % 5. Longitud promedio real (compárala con la entropía: debe ser >= H(X))
    longitudPromedio = numel(bitsComprimidos) / n;
end