#include <memory>
#include <cmath>
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "std_msgs/msg/float64.hpp"


// Retrive Velocity Command to Spin Wheels
class WASDDriver : public rclcpp::Node
{
    public:
        WASDDriver() : Node("velocity_subscriber") {

            publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
            timer_ = this->create_wall_timer(10ms, std::bind(&WSADDriver::driver_callback, this));

        }

    private:
        void driver_callback() {

            auto message = geometry_msgs::msg::Twist();
            
            
        }
};


// Run Subscriber
int main(int argc, char ** argv) {

    rclcpp::init(argc, argv);
    auto node = std::make_shared<WASDDriver>();
    rclcpp::spin(node);
    rclcpp::shutdown();

    return 0;
}