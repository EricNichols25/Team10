package main

import (
	"fmt"
	"os"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()


	app.Static("/", "./public/")

	app.Get("/images/:imageName", func(c *fiber.Ctx) error {
		imageName := c.Params("imageName")
		return c.SendFile("./public/images/" + imageName + ".png")
	})

	app.Post("/upload", func(c *fiber.Ctx) error {
		fmt.Println("Upload endpoint hit")

		// Get first file from form field "file"
		file, err := c.FormFile("file")
		if err != nil {
			return err
		}

		fmt.Printf("Received file: %+v\n", file.Filename)

		dir := "./public/images"
		err = os.MkdirAll(dir, os.ModePerm)

		if err != nil {
			fmt.Printf("Error creating directory: %v\n", err)
		} else {
			fmt.Printf("Directory '%s' created successfully (or already existed).\n", dir)
		}

		// Save file to root directory
		err = c.SaveFile(file, fmt.Sprintf("./public/images/%s", file.Filename))
		if err != nil {
			return err
		}

		fmt.Println("File saved successfully")

		return c.SendString(fmt.Sprintf("File %s uploaded successfully.", file.Filename))
	})

	// Start server
	app.Listen(":3001")

	fmt.Println("Server is running at http://localhost:3001")
}
