find_package(GTest REQUIRED)

add_executable(tests
    test_basic.cpp
)

target_link_libraries(tests
    heat_transfer_core
    GTest::GTest
    GTest::Main
)

add_test(NAME heat_transfer_tests COMMAND tests)
