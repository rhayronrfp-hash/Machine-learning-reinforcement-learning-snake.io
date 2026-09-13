#include <iostream>
#include <sstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>

double dist_ponto_segmento(double px, double py, double x1, double y1, double x2, double y2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    double comp2 = dx * dx + dy * dy;
    
    if (comp2 < 1e-10) {
        double dax = px - x1;
        double day = py - y1;
        return dax * dax + day * day;
    }
    
    double t = ((px - x1) * dx + (py - y1) * dy) / comp2;
    t = std::max(0.0, std::min(1.0, t));
    
    double cx = x1 + t * dx;
    double cy = y1 + t * dy;
    double dax = px - cx;
    double day = py - cy;
    
    return dax * dax + day * day;
}

int main() {
    std::string linha;
    while (std::getline(std::cin, linha)) {
        if (linha.empty()) continue;
        
        std::istringstream iss(linha);
        int num_cobras;
        double limiar;
        iss >> num_cobras >> limiar;
        
        std::vector<std::vector<int>> colisoes(num_cobras);
        
        for (int i = 0; i < num_cobras; i++) {
            double cabeca_x, cabeca_y;
            int num_segs_i;
            iss >> cabeca_x >> cabeca_y >> num_segs_i;
            
            bool colidiu = false;
            
            for (int j = 0; j < num_cobras && !colidiu; j++) {
                if (i == j) {
                    int dummy_segs;
                    iss >> dummy_segs;
                    for (int k = 0; k < dummy_segs; k++) {
                        double d1, d2, d3, d4;
                        iss >> d1 >> d2 >> d3 >> d4;
                    }
                    continue;
                }
                
                int num_segs_j;
                iss >> num_segs_j;
                
                for (int k = 0; k < num_segs_j && !colidiu; k++) {
                    double x1, y1, x2, y2;
                    iss >> x1 >> y1 >> x2 >> y2;                    
                    double dist = dist_ponto_segmento(cabeca_x, cabeca_y, x1, y1, x2, y2);                                        
                    if (dist < limiar) {
                        colisoes[i].push_back(j);
                        colidiu = true;
                    }
                }
            }
        }
        
        std::cout << num_cobras;
        for (int i = 0; i < num_cobras; i++) {
            std::cout << " " << colisoes[i].size();
            for (int j : colisoes[i]) {
                std::cout << " " << j;
            }
        }
        std::cout << std::endl;
        std::cout.flush();
    }
    
    return 0;
}
