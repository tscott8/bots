require 'bundler'
Bundler.require
require 'rest-client'
require 'json'

# site['posts/1/comments'].post 'Good article.', :content_type => 'text/plain'
$token = ''
#API REQUESTS
def request(endpoint, params={})
  site = 'http://battleship.inseng.net/' + endpoint
  x_token = { :'X-Token' => $token }
  response = RestClient.post(site, params, x_token)
  puts response.body
  puts response.code
  response = JSON.parse(response.body)
  return response
end

def createGame
  data = request("games")
  puts "gameID:#{data['id']}"
  return data
end

def addPlayer(gameID, params)
  data = request("games/#{gameID}/players", params)
  return data
end

def move(gameID, params)
  coordinate = {move:params}
  data = request("games/#{gameID}/moves", coordinate)
  return data
end

#BRAIN
def buildPlayer(name='TylerBot')
  ships = setupShips
  player = {name: name , match: 'true'}
  player.merge!(ships)
  puts player
  return player
end

def setupShips(ships=nil)
  default = {
    carrierCell: 'B2',
    carrierDirection: 'left',
    battleshipCell: 'H4',
    battleshipDirection: 'down',
    destroyerCell: 'C8',
    destroyerDirection: 'left',
    cruiserCell: 'E5',
    cruiserDirection: 'down',
    submarineCell: 'I9',
    submarineDirection: 'left',
  } unless ships
  return ships||default
end

def setupGame(gameID=nil)
  game = createGame unless gameID
  player = buildPlayer()
  data = addPlayer(gameID||game['id'],player)
  return data
end

# def t800(moves)
# #check vertical
#   hits = []
#   coordinate = ''
#   moves.each_with_index do |row,i|
#     row.each_with_index do |value,j|
#       if value == 1
#         #check top bottom left right
#         if moves[i][j].nil?
#
#         c = (j+66).chr
#         r = i+1
#         coordinate = "#{c}#{r}"
#         if ()
#         available.push coordinate
#       end
#     end
#   end
#   hits
# #check horizontal
# end

def moveIncrememtally(j=0, i=0)
 if j < 11
   j+=1
 end
if j == 11 && i < 11
  i+=1
end
  c = (j+65).chr
  r = i
  coordinate = "#{c}#{r}"
  return coordinate
end

def availableMoves(moves)
  available = []
  coordinate = ''
  moves.each_with_index do |row,i|
    row.each_with_index do |value,j|
      if value.nil?
          c = (j+66).chr
          r = i+1
          coordinate = "#{c}#{r}"
          available.push coordinate
      end
    end
  end
  available
end


def playGame
  game = setupGame()
  $token = game['currentPlayer']['token']
  moves = game['currentPlayer']['moves']
  i=0
  j=0
  while game['state'] != 'FINISHED' do
    available = availableMoves(moves)
    coordinate = moveIncrememtally(i,j)
    update_moves = move(game['id'], coordinate)

    # puts game['players'].find { |me| me['name']=='TylerBot'}['moves']
    # attack = t800(moves)
    #if attack is nil or impossible do this
    # update_moves = move(game['id'], available.sample)
    #else do this
    # update_moves = move(game['id'], attack)
    moves = update_moves['currentPlayer']['moves']
  end
end

playGame
