workspace {
    model {
        user = person "Пользователь умного дома"

        smart_home = softwareSystem "Умный дом" {

        }

        user -> smart_home "Использует умный дом"

    }

    views {

        themes default

        systemContext smart_home "Context" {
            include *
            autoLayout
        }
        
    }
}