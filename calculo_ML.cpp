#include <iostream>
#include "/storage/emulated/0/eigen-3.4.0/Eigen/Dense"
#include <deque>
#include <sstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <random>
#include <fstream>
using namespace std;
using namespace Eigen;
const char *arqm = "melhor_ia.txt";
const double epsilon_inicial = 1.0;
const double epsilon_final = 0.1;
const double decaimento_epsilon = 0.00001;
const double gama = 0.98;

struct experienciaa
{
    MatrixXd estado;
    int acao;
    double recompensa;
    MatrixXd novo_estado;
    bool morto;
};
struct Calculo
{
  public:
    MatrixXd pesos[3];
    MatrixXd biases[3];
    MatrixXd pesos_target[3];
    MatrixXd biases_target[3];

    bool iniciali = false;
    int contador=0;
    static const int contadormax = 1000;
    deque<experienciaa> buffer;
    static const int limitebf = 10000;

    void inicializar(mt19937 &gen)
{
    pesos[0] = MatrixXd(24, 15);
    pesos[1] = MatrixXd(24, 24);
    pesos[2] = MatrixXd(3, 24);

    biases[0] = MatrixXd(24, 1);
    biases[1] = MatrixXd(24, 1);
    biases[2] = MatrixXd(3, 1);
    buffer.clear();
    contador = 0;
    int acao = 0;
    for (int camada = 0; camada < 3; camada++) {
        double desvio = sqrt(2.0 / pesos[camada].cols());
        normal_distribution<double> dist(0.0, desvio);
        for (int i = 0; i < pesos[camada].rows(); i++){
            for (int j = 0; j < pesos[camada].cols(); j++)
            {
                pesos[camada](i, j) = dist(gen);
            }
        }
        biases[camada].setZero();
    }

    for (int camada = 0; camada < 3; camada++)
    {
        pesos_target[camada] = pesos[camada];
        biases_target[camada] = biases[camada];
    }
    iniciali = true;
}

    int rede_neural(MatrixXd valor_in, mt19937 &gen, double epsilon)
    {
        MatrixXd z1 = pesos[0] * valor_in + biases[0];
        MatrixXd camada1 = z1.cwiseMax(0);

        MatrixXd z2 = pesos[1] * camada1 + biases[1];
        MatrixXd camada2 = z2.cwiseMax(0);

        MatrixXd z3 = pesos[2] * camada2 + biases[2];
        MatrixXd camada3 = z3;

        uniform_real_distribution<double> probabilidade(0.0, 1.0);
        uniform_int_distribution<int> acao_aleatoria(0, 2);

        int indice;
        if (probabilidade(gen) < epsilon)
        {
            indice = acao_aleatoria(gen);
        }
        else
        {
            camada3.col(0).maxCoeff(&indice);
        }

        return indice;
    }
    void addexp(const MatrixXd &estado, int acao, double recompensa, const MatrixXd &novo_estado, bool morto)
    {
        if (buffer.size() >= limitebf)
        {
            buffer.pop_front();
        }
        buffer.push_back({estado, acao, recompensa, novo_estado, morto});
    }
    void treinar_experiencia(const experienciaa &experiencia)
    {
        MatrixXd z1 = pesos[0] * experiencia.estado + biases[0];
        MatrixXd camada1 = z1.cwiseMax(0);
        MatrixXd z2 = pesos[1] * camada1 + biases[1];
        MatrixXd camada2 = z2.cwiseMax(0);
        MatrixXd z3 = pesos[2] * camada2 + biases[2];        
        
        MatrixXd z1n = pesos_target[0] * experiencia.novo_estado + biases_target[0];
        MatrixXd camada1n = z1n.cwiseMax(0);
        MatrixXd z2n = pesos_target[1] * camada1n + biases_target[1];
        MatrixXd camada2n = z2n.cwiseMax(0);
        MatrixXd z3n = pesos_target[2] * camada2n + biases_target[2];

        MatrixXd z1n_online = pesos[0] * experiencia.novo_estado + biases[0];
        MatrixXd camada1n_online = z1n_online.cwiseMax(0);
        MatrixXd z2n_online = pesos[1] * camada1n_online + biases[1];
        MatrixXd camada2n_online = z2n_online.cwiseMax(0);
        MatrixXd z3n_online = pesos[2] * camada2n_online + biases[2];
        int indicen;
        z3n_online.col(0).maxCoeff(&indicen);
        double qnovo = z3n(indicen, 0);
        double qacao = z3(experiencia.acao, 0);
        double queremos;
        if (experiencia.morto){
            queremos= experiencia.recompensa;}
        else
        {
            queremos = experiencia.recompensa + gama * qnovo;}
        double erro = qacao - queremos;
        erro = max(-10.0, min(10.0, erro));

        MatrixXd dz3 = MatrixXd::Zero(3, 1);
        dz3(experiencia.acao, 0) = 2 * erro;
        MatrixXd gradiente_pesos3 = dz3 * camada2.transpose();
        gradiente_pesos3 = gradiente_pesos3.cwiseMax(-5).cwiseMin(5);
        MatrixXd gradiente_bias3 = dz3;
        gradiente_bias3 = gradiente_bias3.cwiseMax(-5).cwiseMin(5);

        MatrixXd dz2 = pesos[2].transpose() * dz3;
        for (int i = 0; i < dz2.rows(); i++)
        {
            if (z2(i, 0) <= 0)
                dz2(i, 0) = 0;
        }

        MatrixXd gradiente_pesos2 = dz2 * camada1.transpose();
        gradiente_pesos2 = gradiente_pesos2.cwiseMax(-5).cwiseMin(5);
        MatrixXd gradiente_bias2 = dz2;
        gradiente_bias2 = gradiente_bias2.cwiseMax(-5).cwiseMin(5);

        MatrixXd dz1 = pesos[1].transpose() * dz2;
        for (int i = 0; i < dz1.rows(); i++)
        {
            if (z1(i, 0) <= 0)
                dz1(i, 0) = 0;
        }
        MatrixXd gradiente_pesos1 = dz1 * experiencia.estado.transpose();
        gradiente_pesos1 = gradiente_pesos1.cwiseMax(-5).cwiseMin(5);
        MatrixXd gradiente_bias1 = dz1;
        gradiente_bias1 = gradiente_bias1.cwiseMax(-5).cwiseMin(5);

        pesos[0] -= 0.01 * gradiente_pesos1;
        pesos[1] -= 0.01 * gradiente_pesos2;
        pesos[2] -= 0.01 * gradiente_pesos3;
        biases[0] -= 0.01 * gradiente_bias1;
        biases[1] -= 0.01 * gradiente_bias2;
        biases[2] -= 0.01 * gradiente_bias3;
    }
    void treino(const MatrixXd &estado, int acao, MatrixXd nestado, double recompensa, mt19937 &gen, bool morto)
    {
        addexp(estado, acao, recompensa, nestado, morto);
        for (int i = 0; i < 4; i++)
    {
        uniform_int_distribution<int> distribuicao(0, buffer.size() - 1);
        int indice = distribuicao(gen);
        treinar_experiencia(buffer[indice]);
    }
        contador++;
        if (contador >= contadormax){
            for (int c = 0; c < 3; c++){
                pesos_target[c] = pesos[c];
                biases_target[c] = biases[c];}
            contador = 0;
        }
    }
};

void salvar(Calculo &c, const string &caminho, double epsilon_atual)
{
    ofstream out(caminho);
    if (!out.good())
        return;

    for (int camada = 0; camada < 3; camada++)
        for (int i = 0; i < c.pesos[camada].rows(); i++)
            for (int j = 0; j < c.pesos[camada].cols(); j++)
                out << c.pesos[camada](i, j) << " ";

    for (int camada = 0; camada < 3; camada++)
        for (int i = 0; i < c.biases[camada].rows(); i++)
            out << c.biases[camada](i, 0) << " ";

    out << epsilon_atual << " ";

    out.close();
}

bool carregar(Calculo &c, const string &caminho, double &epsilon_out)
{
    ifstream in(caminho);
    if (!in.good())
        return false;

    c.pesos[0] = MatrixXd(24, 15);
    c.pesos[1] = MatrixXd(24, 24);
    c.pesos[2] = MatrixXd(3, 24);
    c.biases[0] = MatrixXd(24, 1);
    c.biases[1] = MatrixXd(24, 1);
    c.biases[2] = MatrixXd(3, 1);

    for (int camada = 0; camada < 3; camada++)
        for (int i = 0; i < c.pesos[camada].rows(); i++)
            for (int j = 0; j < c.pesos[camada].cols(); j++)
                in >> c.pesos[camada](i, j);

    for (int camada = 0; camada < 3; camada++)
        for (int i = 0; i < c.biases[camada].rows(); i++)
            in >> c.biases[camada](i, 0);

    bool ok = !in.fail();

    double epsilon_lido;
    if (ok && (in >> epsilon_lido))
    {
        epsilon_out = epsilon_lido;
    }

    in.close();

    if (ok){
        c.buffer.clear();
    c.contador = 0;

    for (int camada = 0; camada < 3; camada++)
{
    c.pesos_target[camada] = c.pesos[camada];
    c.biases_target[camada] = c.biases[camada];
}
        c.iniciali = true;
    }
    return ok;
}

struct Segmento
{
    double x1, y1, x2, y2;
};

double comprimento_segmento(const Segmento &seg)
{
    double dx = seg.x2 - seg.x1;
    double dy = seg.y2 - seg.y1;
    return sqrt(dx * dx + dy * dy);
}

double dist_ponto_segmento(double px, double py, const Segmento &seg)
{
    double dx = seg.x2 - seg.x1;
    double dy = seg.y2 - seg.y1;
    double comp2 = dx * dx + dy * dy;

    if (comp2 < 1e-10)
    {
        double dax = px - seg.x1;
        double day = py - seg.y1;
        return dax * dax + day * day;
    }
    double t = ((px - seg.x1) * dx + (py - seg.y1) * dy) / comp2;
    t = max(0.0, min(1.0, t));
    double cx = seg.x1 + t * dx;
    double cy = seg.y1 + t * dy;
    double dax = px - cx;
    double day = py - cy;

    return dax * dax + day * day;
}

int main()
{
    random_device rd;
    mt19937 gen(rd());
    double epsilon = epsilon_inicial;

    Calculo calculo;
    vector<int> ac;
    string linha;
    while (getline(cin, linha))
    {
        if (linha.empty())
            continue;

        istringstream iss(linha);
        int tipo;
        iss >> tipo;

        if (tipo == 0)
        {
            calculo.inicializar(gen);
            cout << "OK" << endl;
            cout.flush();
        }
        else if (tipo == 2)
        {
            double epsilon_salvar;
            iss >> epsilon_salvar;
            if (calculo.iniciali)
                salvar(calculo, arqm, epsilon_salvar);
            cout << "OK" << endl;
            cout.flush();
        }
        else if (tipo == 3)
        {
            double epsilon_lido = epsilon;
            bool ok = carregar(calculo, arqm, epsilon_lido);
            if (ok)
            {
                epsilon = max(epsilon_final, epsilon_lido);
            }
            cout << (ok ? "OK" : "FAIL") << endl;
            cout.flush();
        }
        else if (tipo == 4)
        {
            double novo;
            iss >> novo;
            epsilon = novo;
            cout << "OK" << endl;
            cout.flush();
        }
        else if (tipo == 5)
        {
            int num_cobras;
            double limiar;
            iss >> num_cobras >> limiar;

            vector<vector<Segmento>> todos_segmentos(num_cobras);
            vector<double> cabeca_x(num_cobras);
            vector<double> cabeca_y(num_cobras);

            for (int i = 0; i < num_cobras; i++)
            {
                int num_segs;
                iss >> cabeca_x[i] >> cabeca_y[i] >> num_segs;

                for (int k = 0; k < num_segs; k++)
                {
                    Segmento seg;
                    iss >> seg.x1 >> seg.y1 >> seg.x2 >> seg.y2;
                    todos_segmentos[i].push_back(seg);
                }
            }
            vector<vector<pair<int, int>>> colisoes(num_cobras);
            for (int i = 0; i < num_cobras; i++)
{
    for (int j = 0; j < num_cobras; j++)
    {
        if (i == j)
        {
            continue;
        }
        double dx = cabeca_x[i] - cabeca_x[j];
        double dy = cabeca_y[i] - cabeca_y[j];
        double dist_cabecas = dx * dx + dy * dy;

        if (dist_cabecas < limiar * limiar)
        {
            colisoes[i].push_back({j, 1});
            continue;
        }

        for (const Segmento &seg : todos_segmentos[j])
        {
            double dist = dist_ponto_segmento(cabeca_x[i], cabeca_y[i], seg);

            if (dist < limiar * limiar)
            {
                colisoes[i].push_back({j, 0});
                break;
            }
        }}}
            cout << num_cobras;
for (int i = 0; i < num_cobras; i++)
{
    cout << " " << colisoes[i].size();

    for (auto [j, tipo_colisao] : colisoes[i])
        cout << " " << j << " " << tipo_colisao;
}
cout << endl;
cout.flush();}
        else if (tipo == 7)
        {
            int n;
            iss >> n;
            vector<int> acoes(n);

            for (int k = 0; k < n; k++)
            {
                int id;
                iss >> id;
                MatrixXd valor(15, 1);
                for (int i = 0; i < 15; i++)
                    iss >> valor(i, 0);

                if (!calculo.iniciali)
                {
                    acoes[k] = 0;
                }
                else
                {
                    acoes[k] = calculo.rede_neural(valor, gen, epsilon);                }
            }
            cout << n;
            for (int k = 0; k < n; k++)
                cout << " " << acoes[k];
            cout << endl;
            cout.flush();
        }
        else if (tipo == 6)
        {
            int n;
            iss >> n;
        
            for (int k = 0; k < n; k++)
            {
                int id;
                int acao;
                bool morto;
                double recompensa;
                iss >> id;
                MatrixXd estado(15, 1);
                for (int i = 0; i < 15; i++)
                    iss >> estado(i, 0);
                iss >> acao >> recompensa;
                MatrixXd nestado(15, 1);
                
                for (int i = 0; i < 15; i++)
                    iss >> nestado(i, 0);               
                iss >> morto;
                if (calculo.iniciali)
                    calculo.treino(estado, acao, nestado, recompensa, gen, morto);
            }
            cout << "OK" << endl;
            cout.flush();
        }
        else if (tipo == 8)
        {
            cout << epsilon << endl;
            cout.flush();
        }
        else
        {
            cout << "ERRO" << endl;
            cout.flush();
        }                 
        }    

    return 0;
}