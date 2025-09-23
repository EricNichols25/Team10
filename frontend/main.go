package main

import (
	"fmt"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	// app.Get("/", func(c *fiber.Ctx) error {
	// return c.SendString("Hello, World!")
	// })

	app.Static("/", "./public/")

	app.Get("/images/:imageName", func(c *fiber.Ctx) error {
		imageName := c.Params("imageName")
		return c.SendFile("./public/images/" + imageName + ".png")
	})

	// Start server
	app.Listen(":3001")

	fmt.Println("Server is running at http://localhost:3001")
}
