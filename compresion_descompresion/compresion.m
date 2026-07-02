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
    codigos = construirArbol(simbolosUnicos, probabilidades);

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

function codigos = construirArbol(simbolos, probabilidades)
    nNodos = numel(simbolos);

    if nNodos == 1
        % Caso trivial: un solo símbolo -> código de 1 bit
        codigos = containers.Map('KeyType','double','ValueType','char');
        codigos(simbolos(1)) = '0';
        return;
    end

    % Cada nodo: simbolo (NaN si es interno), prob, izq/der (índices hijos)
    todos = struct('simbolo', num2cell(simbolos), 'prob', num2cell(probabilidades), ...
                    'izq', num2cell(zeros(1,nNodos)), 'der', num2cell(zeros(1,nNodos)));
    activos = 1:nNodos; % raíces de subárboles aún no combinados

    while numel(activos) > 1
        probsActivos = [todos(activos).prob];
        [~, orden] = sort(probsActivos);
        iMenor   = activos(orden(1));
        iSegundo = activos(orden(2));

        nuevoNodo.simbolo = NaN;
        nuevoNodo.prob = todos(iMenor).prob + todos(iSegundo).prob;
        nuevoNodo.izq = iMenor;
        nuevoNodo.der = iSegundo;
        todos(end+1) = nuevoNodo; %#ok<AGROW>

        activos(orden(1:2)) = [];
        activos(end+1) = numel(todos); %#ok<AGROW>
    end

    raiz = activos(1);
    codigos = containers.Map('KeyType','double','ValueType','char');
    codigos = recorrerArbol(todos, raiz, '', codigos);
end

function codigos = recorrerArbol(todos, indice, prefijo, codigos)
    nodo = todos(indice);
    if nodo.izq == 0 && nodo.der == 0
        if isempty(prefijo)
            prefijo = '0';
        end
        codigos(nodo.simbolo) = prefijo;
    else
        codigos = recorrerArbol(todos, nodo.izq, [prefijo '0'], codigos);
        codigos = recorrerArbol(todos, nodo.der, [prefijo '1'], codigos);
    end
end