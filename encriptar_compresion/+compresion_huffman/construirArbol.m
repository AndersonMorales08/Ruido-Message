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
    codigos = compresion_huffman.recorrerArbol(todos, raiz, '', codigos);
end