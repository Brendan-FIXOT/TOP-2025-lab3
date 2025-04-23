#include <cassert>
#include <cstdlib>

#include <Kokkos_Core.hpp>
#include <fmt/core.h>
#include <Kokkos_Timer.hpp>
#include <string>

using Matrix = Kokkos::View<double**, Kokkos::LayoutRight>;

template <class MatrixType>
auto matrix_init(MatrixType& M) -> void {
  static_assert(2 == MatrixType::rank(), "View must be of rank 2");

  Kokkos::parallel_for(
    "init",
    M.extent(0),
    KOKKOS_LAMBDA(int i) {
      for (int j = 0; j < int(M.extent(1)); ++j) {
        M(i, j) = drand48();
      }
    }
  );
}

template <class AMatrixType, class BMatrixType, class CMatrixType>
auto matrix_product(double alpha, AMatrixType const& A, BMatrixType const& B, double beta, CMatrixType& C) -> void {
  static_assert(
    AMatrixType::rank() == 2 && BMatrixType::rank() == 2 && CMatrixType::rank() == 2, "Views must be of rank 2"
  );
  assert(A.extent(0) == C.extent(0));
  assert(B.extent(1) == C.extent(1));
  assert(A.extent(1) == B.extent(0));

  Kokkos::parallel_for(
    "dgemm_kernel",
    A.extent(0),
    KOKKOS_LAMBDA(int i) {
      for (int j = 0; j < int(B.extent(1)); ++j) {
        double acc = 0.0;
        for (int k = 0; k < int(A.extent(1)); ++k) {
          acc += alpha * A(i, k) * B(k, j);
        }
        C(i, j) *= beta + acc;
      }
    }
  );
}

template <class AMatrixType, class BMatrixType, class CMatrixType>
auto matrix_product_blocked(double alpha, AMatrixType const& A, BMatrixType const& B, double beta, CMatrixType& C, int Bsize) -> void {
  const int M = C.extent(0);
  const int N = C.extent(1);
  const int K = A.extent(1);

  Kokkos::parallel_for("blocked_dgemm", Kokkos::RangePolicy<>(0, M), KOKKOS_LAMBDA(int ii) {
    for (int jj_block = 0; jj_block < N; jj_block += Bsize) {
      for (int kk_block = 0; kk_block < K; kk_block += Bsize) {
        for (int jj = jj_block; jj < jj_block + Bsize && jj < N; ++jj) {
          double acc = 0.0;
          for (int kk = kk_block; kk < kk_block + Bsize && kk < K; ++kk) {
            acc += alpha * A(ii, kk) * B(kk, jj);
          }
          C(ii, jj) *= beta + acc;
        }
      }
    }
  });
}

auto main(int argc, char* argv[]) -> int {
  if (argc < 4) {
    fmt::print("Usage: {} <M> <N> <K>\n", argv[0]);
    return -1;
  }
  int m = std::atoi(argv[1]);
  int n = std::atoi(argv[2]);
  int k = std::atoi(argv[3]);
  std::string layout_arg = argv[4];

  // Known seed for deterministic RNG
  srand48(42);

  Kokkos::initialize(argc, argv);
  {
    if (layout_arg == "right") {
      using Matrix = Kokkos::View<double**, Kokkos::LayoutRight>;

      auto A = Matrix("A", m, k);
      auto B = Matrix("B", k, n);
      auto C = Matrix("C", m, n);

      double alpha = drand48();
      matrix_init(A);
      matrix_init(B);
      double beta = drand48();
      matrix_init(C);

      Kokkos::fence();

      Kokkos::Timer timer; // Pour mesurer le temps de mnaière bien plus précise
      matrix_product(alpha, A, B, beta, C);
      //matrix_product_blocked(alpha, A, B, beta, C, 64); // bloc de taille 64
      Kokkos::fence();
      double elapsed = timer.seconds();
      
      fmt::print("Time: {:.6f} s\n", elapsed);
    } else if (layout_arg == "left") {
      using Matrix = Kokkos::View<double**, Kokkos::LayoutLeft>;

      auto A = Matrix("A", m, k);
      auto B = Matrix("B", k, n);
      auto C = Matrix("C", m, n);

      double alpha = drand48();
      matrix_init(A);
      matrix_init(B);
      double beta = drand48();
      matrix_init(C);

      Kokkos::fence();

      Kokkos::Timer timer; // Pour mesurer le temps de mnaière bien plus précise
      matrix_product(alpha, A, B, beta, C);
      //matrix_product_blocked(alpha, A, B, beta, C, 64); // bloc de taille 64
      Kokkos::fence();
      double elapsed = timer.seconds();
      
      fmt::print("Time: {:.6f} s\n", elapsed);
    } else {
      fmt::print("Layout non renseigné : Utilise 'left' ou 'right'.\n", layout_arg);
      Kokkos::finalize();
      return -1;
    }
  }
  Kokkos::finalize();
  return 0;
}
